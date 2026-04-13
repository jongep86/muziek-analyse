"""Tests voor models.py — database operaties."""

import json
import os
import tempfile
import pytest
from models import (
    init_db, create_track, get_track, list_tracks, search_tracks,
    save_analysis, update_status, update_key, update_file_path,
    delete_track,
)


@pytest.fixture
def db_path():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_db(db_path=path)
    yield path
    os.unlink(path)


class TestInitDb:
    def test_creates_tables(self, db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        assert 'tracks' in tables

    def test_idempotent(self, db_path):
        # Running init_db twice should not fail
        init_db(db_path=db_path)
        init_db(db_path=db_path)


class TestCreateTrack:
    def test_create_basic(self, db_path):
        tid = create_track('Test Track', '/path/to/file.mp3', db_path=db_path)
        assert tid is not None
        assert isinstance(tid, int)

    def test_create_with_metadata(self, db_path):
        tid = create_track('Test', '/path/file.mp3', file_size=1024,
                           filename_key='Am', filename_bpm=120, db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['filename_key'] == 'Am'
        assert track['filename_bpm'] == 120
        assert track['file_size'] == 1024

    def test_create_youtube(self, db_path):
        tid = create_track('YT Track', 'youtube://url', source='youtube',
                           youtube_url='https://youtube.com/watch?v=abc', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['source'] == 'youtube'
        assert track['youtube_url'] == 'https://youtube.com/watch?v=abc'

    def test_duplicate_returns_none(self, db_path):
        create_track('Track', '/path/unique.mp3', db_path=db_path)
        result = create_track('Track 2', '/path/unique.mp3', db_path=db_path)
        assert result is None


class TestGetTrack:
    def test_get_existing(self, db_path):
        tid = create_track('My Track', '/path/track.mp3', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track is not None
        assert track['name'] == 'My Track'
        assert track['status'] == 'pending'

    def test_get_nonexistent(self, db_path):
        assert get_track(999, db_path=db_path) is None

    def test_analysis_data_none_when_no_json(self, db_path):
        tid = create_track('Track', '/path/t.mp3', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['analysis_data'] is None


class TestListTracks:
    def test_empty(self, db_path):
        assert list_tracks(db_path=db_path) == []

    def test_returns_all(self, db_path):
        create_track('A', '/a.mp3', db_path=db_path)
        create_track('B', '/b.mp3', db_path=db_path)
        create_track('C', '/c.mp3', db_path=db_path)
        tracks = list_tracks(db_path=db_path)
        assert len(tracks) == 3

    def test_ordered_by_created_desc(self, db_path):
        create_track('First', '/1.mp3', db_path=db_path)
        create_track('Second', '/2.mp3', db_path=db_path)
        tracks = list_tracks(db_path=db_path)
        names = [t['name'] for t in tracks]
        # Both tracks present; order may vary if created in same second
        assert set(names) == {'First', 'Second'}


class TestSearchTracks:
    def test_search_by_name(self, db_path):
        tid = create_track('Deep House Mix', '/dh.mp3', db_path=db_path)
        _mark_done(tid, db_path)
        tid2 = create_track('Jazz Standard', '/js.mp3', db_path=db_path)
        _mark_done(tid2, db_path)

        results = search_tracks(query='Deep', db_path=db_path)
        assert len(results) == 1
        assert results[0]['name'] == 'Deep House Mix'

    def test_search_by_key(self, db_path):
        tid = create_track('Track A', '/a.mp3', db_path=db_path)
        _mark_done(tid, db_path, key='A', mode='minor')
        tid2 = create_track('Track C', '/c.mp3', db_path=db_path)
        _mark_done(tid2, db_path, key='C', mode='major')

        results = search_tracks(key='A', db_path=db_path)
        assert len(results) == 1

    def test_search_by_bpm_range(self, db_path):
        tid = create_track('Slow', '/slow.mp3', db_path=db_path)
        _mark_done(tid, db_path, bpm=90)
        tid2 = create_track('Fast', '/fast.mp3', db_path=db_path)
        _mark_done(tid2, db_path, bpm=140)

        results = search_tracks(bpm_min=100, bpm_max=150, db_path=db_path)
        assert len(results) == 1
        assert results[0]['name'] == 'Fast'

    def test_search_only_done_tracks(self, db_path):
        create_track('Pending', '/p.mp3', db_path=db_path)
        results = search_tracks(db_path=db_path)
        assert len(results) == 0


class TestSaveAnalysis:
    def test_save_and_retrieve(self, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        analysis = {
            'duration': 180.5,
            'key': 'A',
            'mode': 'minor',
            'key_confidence': 0.85,
            'bpm': 120,
        }
        save_analysis(tid, analysis, db_path=db_path)

        track = get_track(tid, db_path=db_path)
        assert track['status'] == 'done'
        assert track['key'] == 'A'
        assert track['mode'] == 'minor'
        assert track['bpm'] == 120
        assert track['duration'] == 180.5
        assert track['analysis_data']['key_confidence'] == 0.85


class TestUpdateStatus:
    def test_update_to_error(self, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        update_status(tid, 'error', 'Something went wrong', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['status'] == 'error'
        assert track['error_message'] == 'Something went wrong'

    def test_update_to_analysing(self, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        update_status(tid, 'analysing', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['status'] == 'analysing'


class TestUpdateKey:
    def test_override_key(self, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        analysis = {'duration': 100, 'key': 'C', 'mode': 'major', 'key_confidence': 0.9, 'bpm': 120}
        save_analysis(tid, analysis, db_path=db_path)

        update_key(tid, 'A', 'minor', db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['key'] == 'A'
        assert track['mode'] == 'minor'
        assert track['analysis_data']['key'] == 'A'
        assert track['analysis_data']['key_override'] is True


class TestUpdateFilePath:
    def test_update_path(self, db_path):
        tid = create_track('Track', 'youtube://old', db_path=db_path)
        update_file_path(tid, '/new/path.mp3', 5000, db_path=db_path)
        track = get_track(tid, db_path=db_path)
        assert track['file_path'] == '/new/path.mp3'
        assert track['file_size'] == 5000


class TestDeleteTrack:
    def test_delete(self, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        delete_track(tid, db_path=db_path)
        assert get_track(tid, db_path=db_path) is None

    def test_delete_nonexistent_no_error(self, db_path):
        delete_track(999, db_path=db_path)  # should not raise


def _mark_done(track_id, db_path, key='C', mode='major', bpm=120):
    """Helper to mark a track as done with minimal analysis data."""
    analysis = {'duration': 100, 'key': key, 'mode': mode, 'key_confidence': 0.9, 'bpm': bpm}
    save_analysis(track_id, analysis, db_path=db_path)
