import time
from app.config import WHISPER_MODEL
from app.utils.logger import get_logger

logger = get_logger(__name__)
_model = None

def transcribe_audio(audio_path: str) -> dict:
    global _model
    logger.debug(f"Starting transcription for audio path: {audio_path}, model: {WHISPER_MODEL}")
    start_time = time.time()

    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    segments, info = _model.transcribe(audio_path, word_timestamps=True, beam_size=5)

    transcript_segments = []
    all_words = []

    for segment in segments:
        seg_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": []
        }
        if segment.words:
            for w in segment.words:
                word_info = {
                    "word": w.word.strip(),
                    "start": w.start,
                    "end": w.end
                }
                seg_data["words"].append(word_info)
                all_words.append(word_info)
        transcript_segments.append(seg_data)

    elapsed = time.time() - start_time
    logger.debug(f"Transcription completed in {elapsed:.2f}s. Language: {info.language}, total segments: {len(transcript_segments)}, total words: {len(all_words)}")

    return {
        "language": info.language,
        "duration": info.duration,
        "segments": transcript_segments,
        "words": all_words
    }
