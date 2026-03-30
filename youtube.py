"""YouTube download utility via yt-dlp."""

import re
import yt_dlp


# YouTube URL patterns
_YT_PATTERNS = [
    re.compile(r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+'),
    re.compile(r'^https?://youtu\.be/[\w-]+'),
    re.compile(r'^https?://(www\.)?youtube\.com/shorts/[\w-]+'),
    re.compile(r'^https?://music\.youtube\.com/watch\?v=[\w-]+'),
]


def validate_youtube_url(url):
    """Check if the given URL is a valid YouTube URL."""
    return any(p.match(url) for p in _YT_PATTERNS)


def extract_info(url):
    """Extract metadata (title, duration) without downloading."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Onbekend'),
            'duration': info.get('duration', 0),
        }


def download_audio(url, output_dir, progress_callback=None):
    """Download audio from YouTube and convert to mp3.

    Returns dict with file_path, title, duration.
    """
    result = {}

    def _progress_hook(d):
        if d['status'] == 'downloading' and progress_callback:
            pct = d.get('_percent_str', '').strip()
            progress_callback(f"Downloaden... {pct}")
        elif d['status'] == 'finished' and progress_callback:
            progress_callback("Converteren naar mp3...")

    opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [_progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # yt-dlp changes extension after postprocessing
        filename = ydl.prepare_filename(info)
        # Replace original extension with .mp3
        import os
        base, _ = os.path.splitext(filename)
        mp3_path = base + '.mp3'

        result = {
            'file_path': mp3_path,
            'title': info.get('title', 'Onbekend'),
            'duration': info.get('duration', 0),
        }

    return result
