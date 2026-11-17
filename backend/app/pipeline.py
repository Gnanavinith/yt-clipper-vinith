import os
FFMPEG_DIR = r"D:\tools\ffmpeg"
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import time
import sqlite3
import json
from pathlib import Path
from app.config import STORAGE_DIR, CLIPS_DIR, DOWNLOADS_DIR
from app.services.downloader import download_video
from app.services.transcriber import transcribe_audio
from app.services.audio_energy import analyze_audio_energy
from app.services.scenes import detect_scenes
from app.services.highlights import find_highlights
from app.services.cutter import cut_video
from app.services.reframe import reframe_video
from app.services.subtitles import generate_ass_subtitles
from app.services.exporter import burn_subtitles
from app.utils.logger import get_logger, job_id_var

logger = get_logger(__name__)
DB_PATH = STORAGE_DIR / "yt_clipper_raw.db"

def run_pipeline(job_id: str):
    token = None
    try:
        token = job_id_var.set(job_id)
    except Exception:
        pass
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def update_status(status, progress, failed_stage=None, error=None):
        c = sqlite3.connect(DB_PATH)
        c.execute("UPDATE jobs SET status=?, progress=?, failed_stage=?, error=? WHERE id=?", (status, progress, failed_stage, error, job_id))
        c.commit()
        c.close()

    try:
        cursor.execute("SELECT url FROM jobs WHERE id=?", (job_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            if token is not None:
                try:
                    job_id_var.reset(token)
                except Exception:
                    pass
            return
        url = row[0]
        conn.close()

        stages = [
            ("download", 10, lambda: download_video(url, job_id)),
            ("transcribe", 30, lambda: transcribe_audio(download_res["video_path"])),
            ("audio_energy", 40, lambda: analyze_audio_energy(download_res["video_path"])),
            ("scenes", 50, lambda: detect_scenes(download_res["video_path"])),
            ("highlights", 60, lambda: find_highlights(transcript, download_res["heatmap"], audio_energy, scenes)),
            ("cut", 75, None),
            ("reframe", 85, None),
            ("subtitles", 90, None),
            ("export", 95, None)
        ]

        global download_res, transcript, audio_energy, scenes, highlights
        download_res = None
        transcript = None
        audio_energy = None
        scenes = None
        highlights = None

        for stage_name, target_progress, stage_func in stages:
            stage_start = time.time()
            logger.info(f"Starting stage: {stage_name}")
            update_status(stage_name, target_progress)

            try:
                if stage_name == "download":
                    download_res = stage_func()
                elif stage_name == "transcribe":
                    transcript = stage_func()
                elif stage_name == "audio_energy":
                    audio_energy = stage_func()
                elif stage_name == "scenes":
                    scenes = stage_func()
                elif stage_name == "highlights":
                    highlights = stage_func()
                elif stage_name in ["cut", "reframe", "subtitles", "export"]:
                    if stage_name == "cut":
                        job_clips_dir = CLIPS_DIR / job_id
                        job_clips_dir.mkdir(parents=True, exist_ok=True)
                        global processed_clips_data
                        processed_clips_data = []

                        for idx, h in enumerate(highlights):
                            clip_id = f"{job_id}_clip_{idx+1}"
                            start = h["start"]
                            end = h["end"]
                            title = h["title"]
                            score = h["score"]

                            cut_path = str(job_clips_dir / f"cut_{idx+1}.mp4")
                            reframe_path = str(job_clips_dir / f"reframe_{idx+1}.mp4")
                            final_path = str(job_clips_dir / f"clip_{idx+1}.mp4")
                            ass_path = str(job_clips_dir / f"subs_{idx+1}.ass")

                            logger.info(f"Processing clip {idx+1} cut stage ({start}s to {end}s)")
                            cut_video(download_res["video_path"], start, end, cut_path)
                            reframe_video(cut_path, reframe_path)

                            words = transcript.get("words", [])
                            clip_words = [w for w in words if start <= w["start"] <= end or start <= w["end"] <= end]
                            generate_ass_subtitles(clip_words, start, ass_path)
                            burn_subtitles(reframe_path, ass_path, final_path)

                            processed_clips_data.append({
                                "id": clip_id,
                                "job_id": job_id,
                                "title": title,
                                "start_time": start,
                                "end_time": end,
                                "file_path": final_path,
                                "score": score,
                                "subtitles_json": json.dumps(clip_words),
                                "caption_style": "default"
                            })

                stage_elapsed = time.time() - stage_start
                logger.info(f"Finished stage: {stage_name} in {stage_elapsed:.2f}s")

            except Exception as stage_err:
                logger.exception(f"Exception in stage {stage_name}: {stage_err}")
                update_status("failed", target_progress, failed_stage=stage_name, error=str(stage_err))
                if token is not None:
                    try:
                        job_id_var.reset(token)
                    except Exception:
                        pass
                return

        # Save clips to DB
        c_conn = sqlite3.connect(DB_PATH)
        c_cursor = c_conn.cursor()
        for pclip in processed_clips_data:
            c_cursor.execute("""
                INSERT OR REPLACE INTO clips (id, job_id, title, start_time, end_time, file_path, score, subtitles_json, caption_style)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pclip["id"], pclip["job_id"], pclip["title"], pclip["start_time"], pclip["end_time"], pclip["file_path"], pclip["score"], pclip["subtitles_json"], pclip["caption_style"]))
            c_conn.commit()
        c_conn.close()

        update_status("completed", 100)
        logger.info("Pipeline completed successfully for all clips.")

    except Exception as e:
        logger.exception(f"Critical pipeline failure: {e}")
        update_status("failed", 100, failed_stage="pipeline", error=str(e))
    finally:
        if token is not None:
            try:
                job_id_var.reset(token)
            except Exception:
                pass
