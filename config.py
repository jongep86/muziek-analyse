"""Configuratie voor de Muziek-Analyse webapp."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, 'muziek_analyse.db')

# Default audio directory (external disk)
DEFAULT_AUDIO_DIR = '/Volumes/LACIE SHARE/Muziek/___sorted/Deep House/For Trumpet'

# Supported audio extensions
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aiff', '.aif'}

# Output directory for HTML exports
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Flask
SECRET_KEY = 'muziek-analyse-local-dev'
