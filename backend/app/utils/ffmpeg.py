import os
FFMPEG_DIR = r"D:\tools\ffmpeg"
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import subprocess
from app.utils.logger import get_logger

logger = get_logger(__name__)

def run_ffmpeg_cmd(cmd: list):
    cmd_str = " ".join(cmd)
    logger.info(f"Running ffmpeg command: {cmd_str}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        stderr_lines = res.stderr.strip().splitlines()
        last_20 = "\n".join(stderr_lines[-20:])
        logger.error(f"FFmpeg failed with return code {res.returncode}. Last 20 lines of stderr:\n{last_20}")
        raise RuntimeError(f"FFmpeg process failed: {last_20}")
    return res
