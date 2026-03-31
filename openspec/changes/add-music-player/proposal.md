## Why

Users analyze tracks but currently cannot listen to the audio within the web interface — they must switch to external players. Adding an integrated music player enables seamless playback during analysis without context switching, improving the improvisational learning experience.

## What Changes

- Add an HTML5 audio player widget to the track detail page
- Player controls: play/pause, seek/timeline, volume, current time display
- Visual waveform representation (optional, can be simplified)
- Sync audio position with the chord/section timeline so users can hear specific parts while reading analysis
- Support for both uploaded files and YouTube-sourced tracks
- Responsive player design that fits the existing dark theme

## Capabilities

### New Capabilities
- `audio-playback`: Play audio files in the web interface with standard controls (play, pause, seek, volume)
- `audio-timeline-sync`: Highlight and scroll to chord/section in timeline corresponding to current playback position
- `youtube-audio-playback`: Play downloaded YouTube audio tracks with the same player interface

### Modified Capabilities
- `track-detail-view`: Enhance track detail page layout to include audio player widget above or alongside analysis sections

## Impact

- **Frontend**: Add player widget to `templates/track_detail.html`, CSS styling, and JavaScript event listeners
- **Backend**: No API changes needed — uses existing file paths and analysis data
- **Dependencies**: No new external libraries required (HTML5 audio is native)
- **Data**: Requires existing `file_path` (for uploaded tracks) and YouTube download functionality already in place
