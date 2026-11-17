import sqlite3
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid
from app.config import STORAGE_DIR
from app.schemas import JobCreate
from app.pipeline import run_pipeline

router = APIRouter()
DB_PATH = STORAGE_DIR / "yt_clipper_raw.db"

@router.post("/jobs")
def create_job(payload: JobCreate, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jobs (id, url, status, progress) VALUES (?, ?, 'pending', 0)", (job_id, payload.url))
    conn.commit()
    conn.close()

    background_tasks.add_task(run_pipeline, job_id)
    return {"id": job_id, "url": payload.url, "status": "pending", "progress": 0, "failed_stage": None, "error": None, "clips": []}

@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    job_row = cursor.fetchone()
    if not job_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")

    cursor.execute("SELECT * FROM clips WHERE job_id=?", (job_id,))
    clip_rows = cursor.fetchall()
    conn.close()

    clips = []
    for cr in clip_rows:
        fp = Path(cr["file_path"])
        try:
            rel = fp.resolve().relative_to(STORAGE_DIR.resolve())
            video_url = "/storage/" + rel.as_posix()
        except Exception:
            video_url = ""

        clips.append({
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
        })

    return {
        "id": job_row["id"],
        "url": job_row["url"],
        "status": job_row["status"],
        "progress": job_row["progress"],
        "failed_stage": job_row["failed_stage"] if "failed_stage" in job_row.keys() else None,
        "error": job_row["error"],
        "clips": clips
    }

@router.get("/jobs/{job_id}/logs")
def get_job_logs(job_id: str):
    log_file = STORAGE_DIR / "logs" / "app.log"
    if not log_file.exists():
        return {"job_id": job_id, "logs": []}

    matching_logs = []
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if f"job={job_id}" in line or f"job=-" in line:
                matching_logs.append(line.strip())

    return {"job_id": job_id, "logs": matching_logs[-200:]}
