"""Tests voor app.py — Flask routes."""

import os
import tempfile
import pytest
from app import app
from models import init_db, create_track, save_analysis


@pytest.fixture
def db_path(tmp_path):
    """Use a temporary database."""
    path = str(tmp_path / 'test.db')
    init_db(db_path=path)
    return path


@pytest.fixture
def client(db_path, monkeypatch):
    """Flask test client with temporary database."""
    monkeypatch.setattr('app.DB_PATH', db_path)
    monkeypatch.setattr('models.DB_PATH', db_path)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestIndex:
    def test_index_loads(self, client):
        rv = client.get('/')
        assert rv.status_code == 200

    def test_index_with_search(self, client):
        rv = client.get('/?q=test')
        assert rv.status_code == 200


class TestTrackDetail:
    def test_nonexistent_track_redirects(self, client):
        rv = client.get('/tracks/999')
        assert rv.status_code == 302

    def test_pending_track_redirects(self, client, db_path):
        tid = create_track('Test', '/test.mp3', db_path=db_path)
        rv = client.get(f'/tracks/{tid}')
        assert rv.status_code == 302


class TestImportUrlEndpoint:
    def test_import_url_empty(self, client):
        rv = client.post('/import-url', data={'audio_url': ''})
        assert rv.status_code == 302

    def test_import_url_invalid_scheme(self, client):
        rv = client.post('/import-url', data={'audio_url': 'ftp://example.com/a.mp3'})
        assert rv.status_code == 302


class TestRemovedLocalRoutes:
    def test_browse_gone(self, client):
        assert client.get('/browse?folder=/tmp').status_code == 404


class TestDeleteEndpoint:
    def test_delete_track(self, client, db_path):
        tid = create_track('To Delete', '/del.mp3', db_path=db_path)
        rv = client.post(f'/tracks/{tid}/delete')
        assert rv.status_code == 302


class TestOverrideKey:
    def test_override_valid(self, client, db_path):
        tid = create_track('Track', '/t.mp3', db_path=db_path)
        analysis = {'duration': 100, 'key': 'C', 'mode': 'major', 'key_confidence': 0.9, 'bpm': 120}
        save_analysis(tid, analysis, db_path=db_path)
        rv = client.post(f'/tracks/{tid}/override-key', data={'key': 'A', 'mode': 'minor'})
        assert rv.status_code == 302

    def test_override_invalid_key(self, client, db_path):
        tid = create_track('Track', '/t2.mp3', db_path=db_path)
        rv = client.post(f'/tracks/{tid}/override-key', data={'key': 'X', 'mode': 'major'})
        assert rv.status_code == 302


class TestYoutubeImport:
    def test_empty_url(self, client):
        rv = client.post('/youtube', data={'youtube_url': ''})
        assert rv.status_code == 302

    def test_invalid_url(self, client):
        rv = client.post('/youtube', data={'youtube_url': 'https://vimeo.com/123'})
        assert rv.status_code == 302


class TestTemplateFilters:
    def test_fmt_time(self):
        with app.app_context():
            f = app.jinja_env.filters['fmt_time']
            assert f(65) == '1:05'
            assert f(0) == '0:00'
            assert f(None) == '—'

    def test_fmt_size(self):
        with app.app_context():
            f = app.jinja_env.filters['fmt_size']
            assert '1.0 MB' in f(1048576)
            assert f(None) == '—'
