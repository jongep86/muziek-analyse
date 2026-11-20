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
    # Route tests focus on behaviour; CSRF has its own tests below.
    monkeypatch.setitem(app.config, 'WTF_CSRF_ENABLED', False)
    with app.test_client() as client:
        yield client


@pytest.fixture
def csrf_client(db_path, monkeypatch):
    """Flask test client with CSRF protection on, over https so the Secure cookie is sent."""
    monkeypatch.setattr('app.DB_PATH', db_path)
    monkeypatch.setattr('models.DB_PATH', db_path)
    app.config['TESTING'] = True
    monkeypatch.setitem(app.config, 'WTF_CSRF_ENABLED', True)
    with app.test_client() as client:
        client.environ_base['wsgi.url_scheme'] = 'https'
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


def _token_from(html):
    import re
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, 'no csrf_token field rendered'
    return m.group(1)


class TestCsrf:
    def test_every_post_form_has_a_token(self, csrf_client, db_path):
        create_track('Done', '/d.mp3', db_path=db_path)
        html = csrf_client.get('/', base_url='https://localhost').get_data(as_text=True)
        assert html.count('method="POST"') == html.count('name="csrf_token"')

    def test_post_without_token_is_rejected(self, csrf_client, db_path):
        tid = create_track('Keep me', '/keep.mp3', db_path=db_path)
        rv = csrf_client.post(f'/tracks/{tid}/delete', base_url='https://localhost')
        assert rv.status_code == 302
        from models import get_track
        assert get_track(tid, db_path=db_path) is not None

    def test_post_with_token_is_accepted(self, csrf_client, db_path):
        tid = create_track('Delete me', '/gone.mp3', db_path=db_path)
        html = csrf_client.get('/', base_url='https://localhost').get_data(as_text=True)
        token = _token_from(html)
        rv = csrf_client.post(f'/tracks/{tid}/delete', data={'csrf_token': token},
                              base_url='https://localhost',
                              headers={'Referer': 'https://localhost/'})
        assert rv.status_code == 302
        from models import get_track
        assert get_track(tid, db_path=db_path) is None


class TestFetchMetadata:
    def test_cross_site_post_is_forbidden(self, client, db_path):
        tid = create_track('Keep', '/k.mp3', db_path=db_path)
        rv = client.post(f'/tracks/{tid}/delete', headers={'Sec-Fetch-Site': 'cross-site'})
        assert rv.status_code == 403

    def test_same_site_post_is_forbidden(self, client, db_path):
        tid = create_track('Keep', '/k2.mp3', db_path=db_path)
        rv = client.post(f'/tracks/{tid}/delete', headers={'Sec-Fetch-Site': 'same-site'})
        assert rv.status_code == 403

    def test_same_origin_post_passes(self, client, db_path):
        tid = create_track('Go', '/g.mp3', db_path=db_path)
        rv = client.post(f'/tracks/{tid}/delete', headers={'Sec-Fetch-Site': 'same-origin'})
        assert rv.status_code == 302


class TestSecurityHeaders:
    def test_headers_present(self, client):
        rv = client.get('/')
        h = rv.headers
        csp = h['Content-Security-Policy']
        assert "script-src 'nonce-" in csp and "'strict-dynamic'" in csp
        for directive in ("object-src 'none'", "base-uri 'none'", "frame-ancestors 'none'", "form-action 'self'"):
            assert directive in csp
        assert h['X-Frame-Options'] == 'DENY'
        assert h['X-Content-Type-Options'] == 'nosniff'
        assert h['Referrer-Policy'] == 'strict-origin-when-cross-origin'
        assert 'camera=()' in h['Permissions-Policy']
        assert h['Cross-Origin-Opener-Policy'] == 'same-origin'
        assert h['Strict-Transport-Security'].startswith('max-age=')
        assert h['X-Robots-Tag'] == 'noindex, nofollow'

    def test_script_tags_carry_the_nonce(self, client):
        rv = client.get('/')
        csp = rv.headers['Content-Security-Policy']
        nonce = csp.split("'nonce-")[1].split("'")[0]
        html = rv.get_data(as_text=True)
        assert html.count('<script') == html.count(f'nonce="{nonce}"')

    def test_nonce_changes_per_request(self, client):
        a = client.get('/').headers['Content-Security-Policy']
        b = client.get('/').headers['Content-Security-Policy']
        assert a != b

    def test_session_cookie_is_host_prefixed(self):
        assert app.config['SESSION_COOKIE_NAME'] == '__Host-session'
        assert app.config['SESSION_COOKIE_SECURE'] is True
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'


class TestRobots:
    def test_robots_disallows_all(self, client):
        rv = client.get('/robots.txt')
        assert rv.status_code == 200
        assert 'Disallow: /' in rv.get_data(as_text=True)

    def test_no_llms_txt(self, client):
        assert client.get('/llms.txt').status_code == 404


def _done_track(db_path, name='Demo'):
    chords = [{'chord': c, 'start': i * 4.0, 'end': i * 4.0 + 4.0, 'confidence': 0.8}
              for i, c in enumerate(['Cm7', 'Fm7', 'G7', 'Cm7'])]
    data = {'key': 'C', 'mode': 'minor', 'bpm': 120, 'chords': chords,
            'sections': [{'name': 'A', 'start': 0.0, 'end': 16.0, 'chords': chords}],
            'duration': 16.0, 'bars': [{'start': 0.0, 'end': 2.0}], 'key_confidence': 0.8,
            'melody': None}
    tid = create_track(name, f'/{name}.mp3', db_path=db_path)
    save_analysis(tid, data, db_path=db_path)
    return tid


class TestTrackDetailMarkup:
    def test_no_inline_handlers_and_nonced_script(self, client, db_path):
        tid = _done_track(db_path)
        rv = client.get(f'/tracks/{tid}')
        assert rv.status_code == 200
        html = rv.get_data(as_text=True)
        assert 'onclick=' not in html and 'onsubmit=' not in html
        assert '<script nonce="' in html
        assert 'outline: none' not in html

    def test_track_name_cannot_break_out_of_script(self, client, db_path):
        tid = _done_track(db_path, name='x</script><script>alert(1)</script>')
        html = client.get(f'/tracks/{tid}').get_data(as_text=True)
        assert '<script>alert(1)' not in html
