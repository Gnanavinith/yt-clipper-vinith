import os
FFMPEG_DIR = r"D:\tools\ffmpeg"
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import time
import shutil
import subprocess
import yt_dlp
from pathlib import Path
from app.config import DOWNLOADS_DIR
from app.utils.logger import get_logger

logger = get_logger(__name__)

class YTDLPLogger:
    def debug(self, msg):
        if msg.startswith('[debug]'):
            logger.debug(msg)
        else:
            logger.info(msg)
    def info(self, msg):
        logger.info(msg)
    def warning(self, msg):
        logger.warning(msg)
    def error(self, msg):
        logger.error(msg)

def check_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        logger.info(f"FFmpeg located at startup: {ffmpeg_path}")
    else:
        logger.warning("WARNING: ffmpeg not found in PATH! Video cutting and encoding will fail.")

check_ffmpeg()

def download_video(url: str, job_id: str) -> dict:
    job_dir = DOWNLOADS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'bv*+ba/b',
        'outtmpl': str(job_dir / 'source.%(ext)s'),
        'writesubtitles': False,
        'writeautomaticsub': False,
        'subtitleslangs': [],
        'ignoreerrors': 'only_download',
        'quiet': True,
        'logger': YTDLPLogger(),
    }

    logger.info(f"Downloading video from URL: {url} with opts: format=best, writesubtitles=False")

    retries = 3
    backoff = 2
    info = None

    for attempt in range(1, retries + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            break
        except Exception as e:
            err_str = str(e)
            logger.warning(f"Download attempt {attempt} failed: {err_str}")
            if any(code in err_str for code in ["429", "500", "502", "503", "504"]) and attempt < retries:
                sleep_time = backoff ** attempt
                logger.info(f"Transient HTTP error detected. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                if attempt == retries:
                    raise

    if info is None:
        raise RuntimeError("yt-dlp returned no info. Check the log for the real error (429, private video, etc.)")

    video_files = list(job_dir.glob('source.*'))
    video_path = None
    for vf in video_files:
        if vf.suffix in ['.mp4', '.mkv', '.webm', '.mov']:
            video_path = str(vf)
            break

    if not video_path and video_files:
        video_path = str(video_files[0])

    if not video_path or not os.path.exists(video_path):
        raise Exception("Video download failed or file not found.")

    file_size = os.path.getsize(video_path)
    duration = info.get('duration', 0)
    title = info.get('title', 'Untitled')
    heatmap = info.get('heatmap', None)

    logger.info(f"Download completed successfully. Output path: {video_path}, size: {file_size} bytes, duration: {duration}s")
    return {
        "video_path": video_path,
        "heatmap": heatmap,
        "duration": duration,
        "title": title,
        "job_dir": str(job_dir)
    }
