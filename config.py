"""Configuratie voor de Muziek-Analyse webapp."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', BASE_DIR)

# Database
DB_PATH = os.path.join(DATA_DIR, 'muziek_analyse.db')

# Supported audio extensions
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aiff', '.aif'}

# YouTube download directory (same as tracks folder)
YOUTUBE_DOWNLOAD_DIR = os.path.join(DATA_DIR, 'tracks')

# Upload directory for ad-hoc uploaded files (deleted after analysis)
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')

# Max upload size in bytes (100 MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024

# Output directory for HTML exports
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

# Flask
def _load_secret_key():
    """Secret key for sessions and CSRF tokens.

    FLASK_SECRET_KEY wins. Without it a random key is generated once and kept in
    DATA_DIR, so it survives restarts but is never a value that sits in the repo.
    """
    env_key = os.environ.get('FLASK_SECRET_KEY')
    if env_key:
        return env_key
    path = os.path.join(DATA_DIR, '.flask_secret_key')
    try:
        with open(path) as fh:
            key = fh.read().strip()
            if key:
                return key
    except FileNotFoundError:
        pass
    import secrets
    key = secrets.token_hex(32)
    os.makedirs(DATA_DIR, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as fh:
        fh.write(key)
    return key


SECRET_KEY = _load_secret_key()

# Session cookie: Secure (and the __Host- prefix) by default. Set
# SESSION_COOKIE_SECURE=0 only for plain-http local runs on another host than localhost.
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '1') != '0'

# HSTS max-age in seconds. Starts short on purpose; raise it once HTTPS is proven stable.
HSTS_MAX_AGE = int(os.environ.get('HSTS_MAX_AGE', '300'))
