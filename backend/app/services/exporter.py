import subprocess
import time
from pathlib import Path
from app.utils.ffmpeg import run_ffmpeg_cmd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def burn_subtitles(video_path: str, ass_path: str, output_path: str, fonts_dir: str = "assets/fonts") -> str:
    logger.debug(f"Burning subtitles. Video: {video_path}, ASS: {ass_path}, output: {output_path}")
    t_start = time.time()

    ass_path_obj = Path(ass_path).resolve()
    # Resolve absolute path for fonts dir as well if relative
    backend_dir = Path(__file__).resolve().parent.parent.parent
    resolved_fonts_dir = (backend_dir / fonts_dir).resolve()

    # Windows: convert paths to forward slashes and escape colon for ffmpeg filter syntax
    def ffmpeg_escape_path(p: Path) -> str:
        s = str(p).replace("\\", "/")
        if ":" in s:
            drive, rest = s.split(":", 1)
            return f"{drive}\\:/{rest}"
        return s

    ass_str = ffmpeg_escape_path(ass_path_obj)
    fonts_str = ffmpeg_escape_path(resolved_fonts_dir)

    filter_str = f"ass='{ass_str}':fontsdir='{fonts_str}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", filter_str,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "copy",
        output_path
    ]

    try:
        run_ffmpeg_cmd(cmd)
    except Exception as e:
        logger.warning(f"FFmpeg burn with preset/fontsdir failed, fallback to basic ass filter: {e}")
        filter_simple = f"ass=filename='{ass_str}'"
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", filter_simple,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path
        ]
        run_ffmpeg_cmd(cmd_fallback)

    elapsed = time.time() - t_start
    logger.debug(f"Burn subtitles completed in {elapsed:.2f}s.")
    return output_path
