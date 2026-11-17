# YT-Clipper 🎬✂️

YT-Clipper is a local web application that takes a YouTube video link and automatically generates high-engagement vertical highlight clips (Shorts, Reels, TikTok) complete with AI transcription, audio-energy scoring, 9:16 reframing, and burned-in animated subtitles.

## Features
- **YouTube Downloader**: Fetches video, audio, metadata, and heatmap data using `yt-dlp`.
- **AI Transcription**: Word-level timestamps using `faster-whisper` (supports English, Tamil, and multilingual content).
- **Highlight Detection**: Intelligent scoring combining YouTube heatmaps, audio RMS energy (`librosa`), and scene boundaries (`PySceneDetect`).
- **Vertical Reframe**: Automatic 9:16 crop (`1080x1920`) optimized for Shorts & Reels.
- **Subtitles**: Generates `.ass` subtitles with word highlighting and burns them in via `ffmpeg`.
- **Interactive Editor**: React frontend to preview, trim, retitle, change caption styles, and download clips.

## Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, `yt-dlp`, `faster-whisper`, `librosa`, `PySceneDetect`, `ffmpeg`.
- **Frontend**: React, Vite, Tailwind CSS, React Router, Axios.

## Quickstart

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Open App**:
   Navigate to `http://localhost:3000` in your browser.
