import sqlite3
import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import STORAGE_DIR, DOWNLOADS_DIR
from app.schemas import ClipUpdate
from app.services.cutter import cut_video
from app.services.reframe import reframe_video
from app.services.subtitles import generate_ass_subtitles
from app.services.exporter import burn_subtitles
from pathlib import Path

router = APIRouter()
DB_PATH = STORAGE_DIR / "yt_clipper_raw.db"

@router.get("/clips/{clip_id}")
def get_clip(clip_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips WHERE id=?", (clip_id,))
    cr = cursor.fetchone()
    conn.close()

    if not cr:
        raise HTTPException(status_code=404, detail="Clip not found")

    fp = Path(cr["file_path"])
    try:
        rel = fp.resolve().relative_to(STORAGE_DIR.resolve())
        video_url = "/storage/" + rel.as_posix()
    except Exception:
        video_url = ""

    return {
        "id": cr["id"],
        "job_id": cr["job_id"],
        "title": cr["title"],
        "start_time": cr["start_time"],
        "end_time": cr["end_time"],
        "file_path": cr["file_path"],
        "video_url": video_url,
        "score": cr["score"],
        "caption_style": cr["caption_style"],
        "subtitles": json.loads(cr["subtitles_json"]) if cr["subtitles_json"] else []
    }

@router.get("/clips/{clip_id}/download")
def download_clip(clip_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM clips WHERE id=?", (clip_id,))
    cr = cursor.fetchone()
    conn.close()

    if not cr or not cr["file_path"] or not os.path.exists(cr["file_path"]):
        raise HTTPException(status_code=404, detail="Clip file not found")

    return FileResponse(cr["file_path"], media_type="video/mp4", filename=f"{clip_id}.mp4")

@router.patch("/clips/{clip_id}")
def update_clip(clip_id: str, payload: ClipUpdate):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips WHERE id=?", (clip_id,))
    cr = cursor.fetchone()

    if not cr:
        conn.close()
        raise HTTPException(status_code=404, detail="Clip not found")

    title = payload.title if payload.title is not None else cr["title"]
    caption_style = payload.caption_style if payload.caption_style is not None else cr["caption_style"]
    start_time = payload.start_time if payload.start_time is not None else cr["start_time"]
    end_time = payload.end_time if payload.end_time is not None else cr["end_time"]
    subtitles_json = cr["subtitles_json"]

    re_render = False
    if payload.start_time is not None and payload.start_time != cr["start_time"]:
        re_render = True
    if payload.end_time is not None and payload.end_time != cr["end_time"]:
        re_render = True
    if payload.subtitles is not None:
        subtitles_json = json.dumps([s.dict() for s in payload.subtitles])
        re_render = True

    cursor.execute("""
        UPDATE clips SET title=?, caption_style=?, start_time=?, end_time=?, subtitles_json=? WHERE id=?
    """, (title, caption_style, start_time, end_time, subtitles_json, clip_id))
    conn.commit()
    conn.close()

    if re_render:
        job_id = cr["job_id"]
        job_dir = Path(cr["file_path"]).parent
        source_dir = DOWNLOADS_DIR / job_id
        source_videos = list(source_dir.glob("source.*"))
        if source_videos:
            source_path = str(source_videos[0])
            cut_path = str(job_dir / f"cut_{clip_id}.mp4")
            reframe_path = str(job_dir / f"reframe_{clip_id}.mp4")
            ass_path = str(job_dir / f"subs_{clip_id}.ass")
            final_path = cr["file_path"]

            cut_video(source_path, start_time, end_time, cut_path)
            reframe_video(cut_path, reframe_path)

            words = json.loads(subtitles_json) if subtitles_json else []
            generate_ass_subtitles(words, start_time, ass_path, caption_style)
            burn_subtitles(reframe_path, ass_path, final_path)

    return get_clip(clip_id)
