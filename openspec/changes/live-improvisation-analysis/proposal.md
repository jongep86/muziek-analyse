## Why

Musicians improvising with backing tracks often don't know what notes or chords they should play. Real-time audio analysis during improvisation provides immediate feedback on what they're currently playing, helping them understand their choices and improve on the fly.

## What Changes

- Capture live microphone audio during improvisation sessions (5-10 minute bounded sessions)
- Detect and display notes/chords in real-time as the user plays
- Continuously refine chord detection as more audio arrives (rolling updates)
- Support exporting improvisation session results to HTML for review
- Discard session data automatically after the session ends (no persistence)

## Capabilities

### New Capabilities
- `live-audio-capture`: Capture and stream microphone audio from the browser to the server during improvisation sessions
- `real-time-chord-detection`: Detect notes and chords from live audio chunks, with rolling refinement as new data arrives
- `session-management`: Manage time-bounded improvisation sessions (5-10 minutes max) with automatic expiration
- `live-results-display`: Display detected notes and chords in real-time to the user during improvisation
- `session-export`: Export improvisation session results (timeline of detected notes/chords) to HTML for later review

### Modified Capabilities
- `analysis-export`: Extend HTML export to support improvisation session results alongside track analysis results

## Impact

**Frontend:**
- New improvisation/practice mode page with microphone capture controls
- Real-time display of detected notes, chords, and refinement progress
- Session timer UI (5-10 minute countdown)
- Export button to save session results to HTML

**Backend:**
- New WebSocket or chunked HTTP endpoint for receiving live audio streams
- In-memory session state management (no database persistence needed)
- Chord/note detection applied to live audio chunks
- Rolling refinement logic (re-analyze recent audio window as new chunks arrive)

**Dependencies:**
- WebRTC / MediaRecorder API (browser-side, standard)
- librosa for audio analysis (existing)
- Threading for parallel session processing (existing)

**No database schema changes** — sessions are ephemeral, stored only in memory during the 5-10 minute window.
