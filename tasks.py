"""Achtergrond-analyse met threading."""

import os
import threading
import traceback
from models import save_analysis, update_status, update_file_path

# Global state for current task
_state_lock = threading.Lock()
_current = {"track_id": None, "step": ""}
_queue = []
_queue_lock = threading.Lock()
_worker_running = False


def get_status(track_id=None):
    """Get current analysis status. If track_id given, check if it's the active one."""
    with _state_lock:
        if track_id and _current["track_id"] != track_id:
            with _queue_lock:
                pos = next((i for i, t in enumerate(_queue) if t["track_id"] == track_id), -1)
            if pos >= 0:
                return {"active": False, "step": f"In wachtrij (positie {pos + 1})"}
            return {"active": False, "step": ""}
        return {"active": _current["track_id"] is not None, "step": _current["step"]}


def enqueue(track_id, file_path, db_path=None):
    """Add a track to the analysis queue."""
    with _queue_lock:
        _queue.append({"type": "analyse", "track_id": track_id, "file_path": file_path, "db_path": db_path})
    _ensure_worker()


def enqueue_youtube(track_id, youtube_url, output_dir, db_path=None):
    """Add a YouTube download + analysis task to the queue."""
    with _queue_lock:
        _queue.append({
            "type": "youtube",
            "track_id": track_id,
            "youtube_url": youtube_url,
            "output_dir": output_dir,
            "db_path": db_path,
        })
    _ensure_worker()


def _ensure_worker():
    """Start the worker thread if not already running."""
    global _worker_running
    with _state_lock:
        if _worker_running:
            return
        _worker_running = True
    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def _worker():
    """Process queued tasks sequentially."""
    global _worker_running
    while True:
        with _queue_lock:
            if not _queue:
                with _state_lock:
                    _worker_running = False
                    _current["track_id"] = None
                    _current["step"] = ""
                return
            task = _queue.pop(0)

        if task["type"] == "youtube":
            _run_youtube_import(task["track_id"], task["youtube_url"],
                                task["output_dir"], task["db_path"])
        else:
            _run_analysis(task["track_id"], task["file_path"], task["db_path"])


def _run_youtube_import(track_id, youtube_url, output_dir, db_path):
    """Download from YouTube then run analysis."""
    def on_progress(step):
        with _state_lock:
            _current["step"] = step

    with _state_lock:
        _current["track_id"] = track_id
        _current["step"] = "Downloaden starten..."

    try:
        update_status(track_id, 'downloading', db_path=db_path)

        from youtube import download_audio
        result = download_audio(youtube_url, output_dir, progress_callback=on_progress)

        file_path = result['file_path']
        file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else None
        update_file_path(track_id, file_path, file_size, db_path=db_path)

        # Now run analysis
        _run_analysis(track_id, file_path, db_path)
    except Exception as e:
        update_status(track_id, 'error', str(e), db_path=db_path)
        traceback.print_exc()
        with _state_lock:
            _current["track_id"] = None
            _current["step"] = ""


def _run_analysis(track_id, file_path, db_path):
    """Run analysis for a single track."""
    def on_progress(step):
        with _state_lock:
            _current["step"] = step

    with _state_lock:
        _current["track_id"] = track_id
        _current["step"] = "Starten..."

    try:
        update_status(track_id, 'analysing', db_path=db_path)
        from analyse import analyse_track
        analysis_data = analyse_track(file_path, progress_callback=on_progress)
        save_analysis(track_id, analysis_data, db_path=db_path)
    except Exception as e:
        update_status(track_id, 'error', str(e), db_path=db_path)
        traceback.print_exc()
    finally:
        with _state_lock:
            _current["track_id"] = None
            _current["step"] = ""
