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
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'muziek-analyse-local-dev')
