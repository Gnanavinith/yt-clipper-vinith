import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

def format_time_ass(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int(int((seconds - int(seconds)) * 100))
    return f"{hours:d}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

def generate_ass_subtitles(words: list, offset_time: float, output_ass_path: str, style: str = "default") -> str:
    logger.debug(f"Generating ASS subtitles. Total words: {len(words)}, offset: {offset_time}s, output: {output_ass_path}")
    t_start = time.time()

    ass_header = """[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,10,10,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if not chunk:
            continue
        start = chunk[0]["start"] - offset_time
        end = chunk[-1]["end"] - offset_time

        if start < 0:
            start = 0.0
        if end <= start:
            end = start + 1.0

        text = " ".join([w["word"] for w in chunk])
        start_str = format_time_ass(start)
        end_str = format_time_ass(end)

        events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))

    elapsed = time.time() - t_start
    logger.debug(f"Generated ASS subtitles in {elapsed:.2f}s with {len(events)} dialogue events.")
    return output_ass_path
