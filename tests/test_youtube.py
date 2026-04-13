"""Tests voor youtube.py — URL validatie."""

import pytest
from youtube import validate_youtube_url


class TestValidateYoutubeUrl:
    def test_standard_url(self):
        assert validate_youtube_url('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_short_url(self):
        assert validate_youtube_url('https://youtu.be/dQw4w9WgXcQ')

    def test_music_url(self):
        assert validate_youtube_url('https://music.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_shorts_url(self):
        assert validate_youtube_url('https://www.youtube.com/shorts/dQw4w9WgXcQ')

    def test_without_www(self):
        assert validate_youtube_url('https://youtube.com/watch?v=dQw4w9WgXcQ')

    def test_http(self):
        assert validate_youtube_url('http://www.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_invalid_url(self):
        assert not validate_youtube_url('https://vimeo.com/12345')
        assert not validate_youtube_url('not a url')
        assert not validate_youtube_url('')

    def test_playlist_url(self):
        # playlist-only URLs should not match
        assert not validate_youtube_url('https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf')
