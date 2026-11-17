import time
from pathlib import Path
from app.utils.ffmpeg import run_ffmpeg_cmd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def burn_subtitles(video_path: str, ass_path: str, output_path: str) -> str:
    logger.debug(f"Burning subtitles. Video: {video_path}, ASS: {ass_path}, output: {output_path}")
    t_start = time.time()

    ass_path_obj = Path(ass_path).resolve()
    # For FFmpeg filter option value parsing on Windows, escape backslashes and colons properly or use forward slashes with escaped colon
    path_str = str(ass_path_obj).replace("\\", "/")
    if ":" in path_str:
        drive, rest = path_str.split(":", 1)
        ass_path_str = f"{drive}\\:/{rest}"
    else:
        ass_path_str = path_str

    # In ffmpeg filter graphs, filename option values with special characters like colons need escaping or filename= syntax
    filter_str = f"ass=filename='{ass_path_str}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", filter_str,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]
    run_ffmpeg_cmd(cmd)

    elapsed = time.time() - t_start
    logger.debug(f"Burn subtitles completed in {elapsed:.2f}s.")
    return output_path
