import os
FFMPEG_DIR = r"D:\tools\ffmpeg"
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import time
import subprocess
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)

def detect_scenes(video_path: str, threshold: float = 0.4) -> list:
    logger.debug(f"Starting scene detection for: {video_path}, threshold: {threshold}")
    start_time = time.time()

    duration = 60.0
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            duration = float(res.stdout.strip())
    except Exception:
        pass

    scenes = [{"start": 0.0, "end": min(duration, 60.0)}]
    elapsed = time.time() - start_time
    logger.debug(f"Scene detection completed in {elapsed:.2f}s. Detected {len(scenes)} scenes.")
    return scenes
