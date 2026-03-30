"""SQLite database schema en data-access functies."""

import json
import sqlite3
from datetime import datetime

from config import DB_PATH


def get_db(db_path=None):
    """Get a database connection."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path=None):
    """Initialize the database schema."""
    conn = get_db(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tracks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            file_path       TEXT NOT NULL UNIQUE,
            file_size       INTEGER,
            duration        REAL,
            key             TEXT,
            mode            TEXT,
            key_confidence  REAL,
            bpm             INTEGER,
            filename_key    TEXT,
            filename_bpm    INTEGER,
            analysis_json   TEXT,
            status          TEXT DEFAULT 'pending',
            error_message   TEXT,
            analyzed_at     TIMESTAMP,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_tracks_status ON tracks(status);
        CREATE INDEX IF NOT EXISTS idx_tracks_key ON tracks(key);
        CREATE INDEX IF NOT EXISTS idx_tracks_bpm ON tracks(bpm);
    """)
    # Migrate: add source and youtube_url columns if missing
    cursor = conn.execute("PRAGMA table_info(tracks)")
    columns = {row[1] for row in cursor.fetchall()}
    if 'source' not in columns:
        conn.execute("ALTER TABLE tracks ADD COLUMN source TEXT DEFAULT 'local'")
    if 'youtube_url' not in columns:
        conn.execute("ALTER TABLE tracks ADD COLUMN youtube_url TEXT")

    conn.commit()
    conn.close()


def create_track(name, file_path, file_size=None, filename_key=None, filename_bpm=None,
                 source='local', youtube_url=None, db_path=None):
    """Insert a new track. Returns track id, or None if already exists."""
    conn = get_db(db_path)
    try:
        cur = conn.execute(
            """INSERT INTO tracks (name, file_path, file_size, filename_key, filename_bpm, source, youtube_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, file_path, file_size, filename_key, filename_bpm, source, youtube_url)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_track(track_id, db_path=None):
    """Get a single track by id."""
    conn = get_db(db_path)
    row = conn.execute("SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()
    conn.close()
    if row:
        return _row_to_dict(row)
    return None


def list_tracks(db_path=None):
    """List all tracks ordered by creation date."""
    conn = get_db(db_path)
    rows = conn.execute("SELECT * FROM tracks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_tracks(query=None, key=None, bpm_min=None, bpm_max=None, db_path=None):
    """Search tracks with optional filters."""
    conn = get_db(db_path)
    sql = "SELECT * FROM tracks WHERE status = 'done'"
    params = []

    if query:
        sql += " AND name LIKE ?"
        params.append(f"%{query}%")
    if key:
        sql += " AND key = ?"
        params.append(key)
    if bpm_min:
        sql += " AND bpm >= ?"
        params.append(int(bpm_min))
    if bpm_max:
        sql += " AND bpm <= ?"
        params.append(int(bpm_max))

    sql += " ORDER BY created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def save_analysis(track_id, analysis_data, db_path=None):
    """Save analysis results for a track."""
    conn = get_db(db_path)
    conn.execute(
        """UPDATE tracks SET
            duration = ?, key = ?, mode = ?, key_confidence = ?, bpm = ?,
            analysis_json = ?, status = 'done', analyzed_at = ?
           WHERE id = ?""",
        (
            analysis_data['duration'],
            analysis_data['key'],
            analysis_data['mode'],
            analysis_data['key_confidence'],
            analysis_data['bpm'],
            json.dumps(analysis_data, ensure_ascii=False),
            datetime.now().isoformat(),
            track_id,
        )
    )
    conn.commit()
    conn.close()


def update_status(track_id, status, error_message=None, db_path=None):
    """Update track analysis status."""
    conn = get_db(db_path)
    conn.execute(
        "UPDATE tracks SET status = ?, error_message = ? WHERE id = ?",
        (status, error_message, track_id)
    )
    conn.commit()
    conn.close()


def update_key(track_id, key, mode, db_path=None):
    """Manually override the detected key and mode for a track."""
    conn = get_db(db_path)
    # Update the key/mode columns
    conn.execute(
        "UPDATE tracks SET key = ?, mode = ? WHERE id = ?",
        (key, mode, track_id)
    )
    # Also update the analysis_json to keep it in sync
    row = conn.execute("SELECT analysis_json FROM tracks WHERE id = ?", (track_id,)).fetchone()
    if row and row['analysis_json']:
        data = json.loads(row['analysis_json'])
        data['key'] = key
        data['mode'] = mode
        data['key_override'] = True
        conn.execute(
            "UPDATE tracks SET analysis_json = ? WHERE id = ?",
            (json.dumps(data, ensure_ascii=False), track_id)
        )
    conn.commit()
    conn.close()


def update_file_path(track_id, file_path, file_size=None, db_path=None):
    """Update file path and size after download."""
    conn = get_db(db_path)
    conn.execute(
        "UPDATE tracks SET file_path = ?, file_size = ? WHERE id = ?",
        (file_path, file_size, track_id)
    )
    conn.commit()
    conn.close()


def delete_track(track_id, db_path=None):
    """Delete a track from the database."""
    conn = get_db(db_path)
    conn.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
    conn.commit()
    conn.close()


def _row_to_dict(row):
    """Convert a sqlite3.Row to a dict with parsed analysis_json."""
    d = dict(row)
    if d.get('analysis_json'):
        d['analysis_data'] = json.loads(d['analysis_json'])
    else:
        d['analysis_data'] = None
    return d
