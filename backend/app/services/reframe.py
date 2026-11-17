import time
from app.utils.ffmpeg import run_ffmpeg_cmd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def reframe_video(input_path: str, output_path: str, method: str = "center") -> str:
    logger.debug(f"Reframing video input: {input_path}, output: {output_path}, method: {method}")
    t_start = time.time()

    filter_complex = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-c:a", "copy",
        output_path
    ]
    run_ffmpeg_cmd(cmd)

    elapsed = time.time() - t_start
    logger.debug(f"Reframe video completed in {elapsed:.2f}s.")
    return output_path
