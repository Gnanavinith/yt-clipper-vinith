import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "storage"))
DOWNLOADS_DIR = STORAGE_DIR / "downloads"
TRANSCRIPTS_DIR = STORAGE_DIR / "transcripts"
CLIPS_DIR = STORAGE_DIR / "clips"

for d in [STORAGE_DIR, DOWNLOADS_DIR, TRANSCRIPTS_DIR, CLIPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_DIR / 'yt_clipper.db'}")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MAX_CLIP_DURATION = int(os.getenv("MAX_CLIP_DURATION", "60"))
MIN_CLIP_DURATION = int(os.getenv("MIN_CLIP_DURATION", "15"))
