## Context

The application currently supports analyzing uploaded audio files with a two-pass streaming approach (fast pass on first 30-60s, full pass on complete file). Musicians want real-time feedback during improvisation — capturing their microphone, analyzing chord/note detection live, and showing results as they play.

Unlike file upload analysis, this session-based analysis:
- Captures continuous live audio (not a bounded file)
- Has a time limit (5-10 minutes max)
- Is ephemeral (discarded after session ends)
- Requires low-latency results
- Can be exported to HTML for later review

## Goals / Non-Goals

**Goals:**
- Capture microphone audio in real-time and stream to backend
- Detect and display notes/chords with <2-3 second latency
- Continuously refine chord detection as more audio arrives
- Enforce 5-10 minute session duration with automatic expiration
- Export session results to HTML after session completes
- No database persistence (sessions live only in memory)

**Non-Goals:**
- Visualize waveforms or frequency analysis during playback
- Integrate with music player or backing track playback (user listens externally)
- Support distributed multi-server analysis
- Real-time synthesis or audio effects
- Analyze backing track (only user's microphone)

## Decisions

### 1. WebSocket Transport for Audio Streaming
**Decision:** Use WebSocket for client-server audio streaming.

**Rationale:** WebSocket provides low-latency bidirectional communication, allowing server to send analysis results in real-time as they're computed. Avoids HTTP polling overhead and keeps connection persistent for the entire session.

**Alternatives:**
- HTTP chunked transfer: Simpler but higher latency (~500ms roundtrip), not true streaming
- gRPC: Overkill for this use case, more complex
- Server-Sent Events (SSE): One-way only, need separate channel for audio upload

### 2. Browser-Side Audio Capture with MediaRecorder
**Decision:** Use Web Audio API + MediaRecorder to capture microphone in browser.

**Rationale:** MediaRecorder handles encoding and timing, produces standard audio blobs. Simple and reliable. Send compressed chunks to server to minimize bandwidth.

**Alternatives:**
- Raw Web Audio API (ScriptProcessor): More control but more overhead, need to handle encoding
- Third-party library (RecordRTC): Additional dependency

### 3. Chunk-Based Streaming (0.5-1 Second Chunks)
**Decision:** Capture audio in 0.5-1 second chunks, send to server immediately, analyze as they arrive.

**Rationale:** Balance between latency and processing overhead. Smaller chunks (0.5s) = faster feedback (~500ms end-to-end). Larger chunks (1s) = less network/processing overhead. Choose 1 second as default (good latency, manageable overhead).

**Alternatives:**
- Very small chunks (100ms): Lots of overhead, minimal latency improvement
- Large chunks (5s+): Delays feedback, worse user experience
- Variable chunk size based on network: Complexity not worth it

### 4. In-Memory Session State (No Database)
**Decision:** Store active sessions only in memory. Discard at session end.

**Rationale:** Sessions are inherently ephemeral (5-10 min, then gone). No need for persistence. Simplifies architecture, faster access, no database churn. If server restarts during a session, it's acceptable to lose that session.

**Alternatives:**
- Store in database: Adds persistence but unnecessary complexity for ephemeral sessions
- Distributed cache (Redis): Overkill for single-instance app

### 5. Rolling Refinement with Sliding Window
**Decision:** Keep a 30-second sliding window of recent audio. Re-analyze entire window when new chunk arrives.

**Rationale:** Chord detection improves with more context. Re-analyzing last 30s with new data refines previous chord detections. 30 seconds is long enough for context, short enough to re-analyze quickly.

**Implementation:**
- Store decoded audio samples in memory for recent session chunks
- When new chunk arrives, concatenate with last 30s of audio
- Re-run chord detection on full window
- Compare results with previous results → report deltas (new chords, updated confidence, etc.)
- Send only deltas to frontend to minimize traffic

### 6. Reuse Existing Analysis Pipeline
**Decision:** Extend `analyse.py` with a `stream_analyze()` function for real-time chunk analysis.

**Rationale:** Current chord detection (librosa + chroma + chord-extractor) works on any audio segment. Add a streaming wrapper that handles chunks, maintains window, calls existing detection logic.

**Alternatives:**
- Duplicate analysis logic: Code duplication, maintenance burden
- New analysis module: More work, same result

### 7. Session Management with Timeout
**Decision:** Automatically expire sessions after 10 minutes. Allow manual stop before timeout.

**Rationale:** Prevents resource leaks from forgotten sessions. 10 minutes is reasonable for an improvisation session. User can stop early if done.

**Implementation:**
- In-memory dict: `{session_id: {audio_chunks: [...], metadata: {...}, created_at: time}}`
- Background task checks for expired sessions every minute
- Endpoint to manually stop/finalize session

### 8. Export Session Results to HTML
**Decision:** After session ends, generate HTML export similar to track analysis HTML.

**Rationale:** Users want to review what they played and detected chords after the session. Standard HTML export provides archival and sharing.

**Format:** Timeline of detected notes/chords over time, styled similarly to track detail HTML.

## Risks / Trade-offs

**[Microphone privacy]** → User explicitly grants microphone access via browser permission. Ensure clear messaging about what audio is captured and how it's used.

**[Audio quality/codec]** → Browser encodes audio (usually Opus or MP3). Quality depends on user's codec choice. May affect chord detection accuracy.

**[Latency spikes]** → Network congestion or server load can cause delays in results. Mitigate with progress indicators and clear messaging.

**[Chord detection on monophonic input]** → Current chord detector works best on polyphonic (multi-note) audio. Monophonic input (single instrument) may have lower accuracy. Mitigation: Test with typical improvisation scenarios, label results as "preliminary" until more audio arrives.

**[Memory usage]** → Keeping 30-second audio window + multiple concurrent sessions could consume RAM. Mitigation: Limit concurrent sessions (e.g., 5 max), periodically trim old audio samples.

**[Export large HTML]** → A 10-minute session with chords every 0.5s = 1200 chord events. HTML export could be large (~2-5 MB). Acceptable for most browsers.

## Migration Plan

1. **Phase 1 (Backend only):**
   - Add WebSocket endpoint for audio streaming
   - Implement `stream_analyze()` in `analyse.py`
   - Session management in-memory dict
   - No frontend changes yet

2. **Phase 2 (Frontend UI):**
   - Add improvisation/practice mode page
   - Microphone capture with MediaRecorder
   - Real-time results display
   - Session timer and stop button

3. **Phase 3 (Export):**
   - Generate HTML export after session
   - Add export button to session results

## Open Questions

1. Should users be able to pause/resume a session within the 10-minute window, or is it all-or-nothing?
2. What's the minimum audio length to export (e.g., at least 1 minute played before allowing export)?
3. Should we show confidence levels for detected chords in real-time?
4. How many concurrent sessions should the app support (resource limit)?
5. Should session results include metadata like session date/time in the HTML export?
