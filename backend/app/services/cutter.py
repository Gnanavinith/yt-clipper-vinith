import time
from app.utils.ffmpeg import run_ffmpeg_cmd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def cut_video(input_path: str, start_time: float, end_time: float, output_path: str) -> str:
    logger.debug(f"Cutting video input: {input_path}, start: {start_time}s, end: {end_time}s, output: {output_path}")
    t_start = time.time()

    duration = end_time - start_time
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]
    run_ffmpeg_cmd(cmd)

    elapsed = time.time() - t_start
    logger.debug(f"Cut video completed in {elapsed:.2f}s.")
    return output_path
