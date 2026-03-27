"""Achtergrond-analyse met threading."""

import threading
import traceback
from models import save_analysis, update_status

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
                pos = next((i for i, t in enumerate(_queue) if t[0] == track_id), -1)
            if pos >= 0:
                return {"active": False, "step": f"In wachtrij (positie {pos + 1})"}
            return {"active": False, "step": ""}
        return {"active": _current["track_id"] is not None, "step": _current["step"]}


def enqueue(track_id, file_path, db_path=None):
    """Add a track to the analysis queue."""
    with _queue_lock:
        _queue.append((track_id, file_path, db_path))
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
    """Process queued analysis tasks sequentially."""
    global _worker_running
    while True:
        with _queue_lock:
            if not _queue:
                with _state_lock:
                    _worker_running = False
                    _current["track_id"] = None
                    _current["step"] = ""
                return
            track_id, file_path, db_path = _queue.pop(0)

        _run_analysis(track_id, file_path, db_path)


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
