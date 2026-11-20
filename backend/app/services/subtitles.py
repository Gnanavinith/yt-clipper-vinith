import time
import json
from app.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_STYLE = {
    "font": "Montserrat",
    "size": 76,
    "text_color": "#FFFFFF",
    "highlight_color": "#FFD23F",
    "outline_color": "#000000",
    "outline": 5,
    "uppercase": True,
    "position": "bottom",
    "words_per_group": 3,
    "animation": "pop",
}

PRESETS = {
    "default": DEFAULT_STYLE,
    "bold": {
        "font": "Montserrat",
        "size": 76,
        "text_color": "#FFFFFF",
        "highlight_color": "#FFD23F",
        "outline_color": "#000000",
        "outline": 5,
        "uppercase": True,
        "position": "bottom",
        "words_per_group": 3,
        "animation": "pop",
    },
    "clean": {
        "font": "Poppins",
        "size": 64,
        "text_color": "#FFFFFF",
        "highlight_color": "#2DE2E6",
        "outline_color": "#000000",
        "outline": 3,
        "uppercase": False,
        "position": "bottom",
        "words_per_group": 3,
        "animation": "none",
    },
    "impact": {
        "font": "Anton",
        "size": 90,
        "text_color": "#FFFFFF",
        "highlight_color": "#FF3B30",
        "outline_color": "#000000",
        "outline": 6,
        "uppercase": True,
        "position": "bottom",
        "words_per_group": 3,
        "animation": "pop",
    },
    "neon": {
        "font": "Montserrat",
        "size": 76,
        "text_color": "#FFFFFF",
        "highlight_color": "#39FF14",
        "outline_color": "#000000",
        "outline": 5,
        "uppercase": True,
        "position": "bottom",
        "words_per_group": 2,
        "animation": "pop",
    }
}

def _ass_color(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) < 6:
        h = "FFFFFF"
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}&".upper()          # ASS uses BGR order

def _ts(sec: float) -> str:
    sec = max(sec, 0)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def _clean(text: str, upper: bool) -> str:
    text = text.strip().replace("{", "(").replace("}", ")").replace("\n", " ")
    return text.upper() if upper else text

def generate_ass_subtitles(words: list, offset_time: float, output_ass_path: str, style_input = None, width: int = 1080, height: int = 1920) -> str:
    logger.debug(f"Generating ASS subtitles. Total words: {len(words)}, offset: {offset_time}s, output: {output_ass_path}")
    t_start = time.time()

    # Parse style input (can be dict, json string, or preset name string)
    style_dict = DEFAULT_STYLE.copy()
    if isinstance(style_input, dict):
        style_dict.update(style_input)
    elif isinstance(style_input, str):
        if style_input.startswith("{"):
            try:
                parsed = json.loads(style_input)
                if isinstance(parsed, dict):
                    style_dict.update(parsed)
            except Exception:
                pass
        elif style_input in PRESETS:
            style_dict = PRESETS[style_input].copy()

    s = style_dict
    n = max(1, int(s.get("words_per_group", 3)))
    align = 2 if s.get("position", "bottom") == "bottom" else 5      # 2 = bottom centre, 5 = middle
    margin_v = 260 if s.get("position", "bottom") == "bottom" else 0  # keeps captions above Shorts/Reels buttons
    base = _ass_color(s.get("text_color", "#FFFFFF"))
    hi = _ass_color(s.get("highlight_color", "#FFD23F"))
    outline_col = _ass_color(s.get("outline_color", "#000000"))
    font_name = s.get("font", "Montserrat")
    font_size = s.get("size", 76)
    outline_val = s.get("outline", 5)
    uppercase_flag = s.get("uppercase", True)
    animation_type = s.get("animation", "pop")

    lines = [
        "[Script Info]", "ScriptType: v4.00+",
        f"PlayResX: {width}", f"PlayResY: {height}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding",
        f"Style: Default,{font_name},{font_size},{base},{base},{outline_col},&H64000000&,"
        f"-1,0,0,0,100,100,0,0,1,{outline_val},2,{align},60,60,{margin_v},1",
        "", "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    valid_words = [w for w in words if w.get("word", "").strip()]

    for g in range(0, len(valid_words), n):
        group = valid_words[g:g + n]
        for i, w in enumerate(group):
            start = w["start"] - offset_time
            end = (group[i + 1]["start"] if i + 1 < len(group) else w["end"]) - offset_time
            if end <= start:
                end = start + 0.1
            if start < 0:
                start = 0.0

            parts = []
            for j, other in enumerate(group):
                txt = _clean(other["word"], uppercase_flag)
                if j == i:
                    pop = r"\fscx85\fscy85\t(0,90,\fscx112\fscy112)" if animation_type == "pop" else ""
                    parts.append("{\\c" + hi + pop + "}" + txt + "{\\c" + base + r"\fscx100\fscy100}")
                else:
                    parts.append(txt)
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Default,,0,0,0,,{' '.join(parts)}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    elapsed = time.time() - t_start
    logger.debug(f"Generated ASS subtitles in {elapsed:.2f}s with {len(valid_words)} words.")
    return output_ass_path
