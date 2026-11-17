import os
FFMPEG_DIR = r"D:\tools\ffmpeg"
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import sqlite3
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import jobs, clips
from app.config import STORAGE_DIR
from app.utils.logger import get_logger
from app.utils.middleware import log_requests_middleware

logger = get_logger("app")
DB_PATH = STORAGE_DIR / "yt_clipper_raw.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            failed_stage TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add failed_stage column if missing in existing table
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN failed_stage TEXT")
        conn.commit()
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            id TEXT PRIMARY KEY,
            job_id TEXT,
            title TEXT,
            start_time REAL,
            end_time REAL,
            file_path TEXT,
            score REAL,
            subtitles_json TEXT,
            caption_style TEXT DEFAULT 'default',
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="YT-Clipper API", version="1.0.0")

app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

app.middleware("http")(log_requests_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(clips.router, prefix="/api", tags=["Clips"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to YT-Clipper API"}
