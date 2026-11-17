import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

def find_highlights(transcript: dict, heatmap: list, audio_energy: list, scenes: list, max_duration: int = 60, min_duration: int = 15) -> list:
    logger.debug(f"Starting highlight extraction. Max duration: {max_duration}s, min duration: {min_duration}s")
    start_time = time.time()

    words = transcript.get("words", [])
    if not words:
        duration = transcript.get("duration", 60)
        logger.warning("No words found in transcript. Fallback to single highlight.")
        return [{"start": 0.0, "end": min(duration, float(max_duration)), "title": "Highlight 1", "score": 1.0}]

    total_duration = transcript.get("duration", words[-1]["end"])
    chunk_size_words = 30
    step_words = 10

    scored_windows = []
    for i in range(0, len(words), step_words):
        window_words = words[i:i + chunk_size_words]
        if not window_words:
            break
        start_time_w = window_words[0]["start"]
        end_time_w = window_words[-1]["end"]
        duration = end_time_w - start_time_w

        if duration < min_duration:
            if i + chunk_size_words < len(words):
                end_time_w = words[min(i + chunk_size_words * 2, len(words) - 1)]["end"]
                duration = end_time_w - start_time_w

        if duration > max_duration:
            end_time_w = start_time_w + max_duration
            duration = max_duration

        window_energies = [e["energy"] for e in audio_energy if start_time_w <= e["time"] <= end_time_w]
        avg_energy = sum(window_energies) / len(window_energies) if window_energies else 0.5

        heatmap_score = 0.5
        if heatmap:
            hm_vals = [h.get("value", 0) for h in heatmap if start_time_w <= h.get("start_time", 0) <= end_time_w]
            if hm_vals:
                heatmap_score = sum(hm_vals) / len(hm_vals)

        score = (avg_energy * 0.5) + (heatmap_score * 0.5)
        scored_windows.append({
            "start": start_time_w,
            "end": end_time_w,
            "score": score,
            "title": f"Highlight @ {int(start_time_w)}s"
        })

    scored_windows.sort(key=lambda x: x["score"], reverse=True)
    selected_clips = []

    for w in scored_windows:
        overlap = False
        for sc in selected_clips:
            if not (w["end"] <= sc["start"] or w["start"] >= sc["end"]):
                overlap = True
                break
        if not overlap:
            selected_clips.append(w)
        if len(selected_clips) >= 3:
            break

    if not selected_clips:
        selected_clips.append({
            "start": 0.0,
            "end": min(total_duration, float(max_duration)),
            "score": 1.0,
            "title": "Main Highlight"
        })

    selected_clips.sort(key=lambda x: x["start"])
    elapsed = time.time() - start_time
    logger.debug(f"Highlight extraction completed in {elapsed:.2f}s. Selected {len(selected_clips)} clips.")
    return selected_clips
