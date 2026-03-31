## 1. Backend: WebSocket Endpoint & Session Management

- [ ] 1.1 Add WebSocket endpoint to `app.py` for audio streaming
  - Route: `/ws/improvise` for WebSocket connection
  - Accept audio chunks (binary format) from client
  - Establish WebSocket connection on session start
- [ ] 1.2 Create session state management in-memory dictionary
  - `sessions = {session_id: {audio_chunks: [], metadata: {}, created_at: time, status: 'active'}}`
  - Generate unique session_id for each connection
  - Store decoded audio samples for rolling window analysis
- [ ] 1.3 Implement session timeout logic
  - Background task that checks for expired sessions every 30 seconds
  - Sessions auto-expire after 10 minutes
  - Clean up expired session data from memory
- [ ] 1.4 Implement session stop/finalize endpoint
  - POST `/sessions/<session_id>/stop` endpoint
  - Freezes session (no more chunks accepted)
  - Returns session metadata and ready for export
- [ ] 1.5 Add session cleanup on graceful shutdown
  - Ensure all sessions are properly closed
  - Prevent memory leaks on server restart

## 2. Backend: Audio Analysis Pipeline

- [ ] 2.1 Create `stream_analyze()` function in `analyse.py`
  - Input: audio chunk (binary) + session state (30s window)
  - Output: detected notes, detected chords, confidence scores
  - Reuse existing chord detection logic (librosa, chroma, chord-extractor)
- [ ] 2.2 Implement rolling window refinement
  - Maintain 30-second sliding window of decoded audio
  - When new chunk arrives, re-analyze entire window
  - Compare previous chord results with new results
  - Return only deltas (what changed) to minimize traffic
- [ ] 2.3 Add note-by-note detection
  - Use pitch detection (e.g., librosa's `piptrack` or similar) on audio chunk
  - Return detected notes with timestamps
  - Handle both monophonic (single note) and polyphonic input
- [ ] 2.4 Implement confidence scoring
  - For each detected chord, calculate confidence percentage
  - Based on signal clarity, frequency power, harmonic consistency
  - Return confidence with results
- [ ] 2.5 Handle silence and noise gracefully
  - Detect silence (low RMS energy) in chunks
  - Skip analysis or mark as "listening..." for silent periods
  - Don't report false-positive chords on noise

## 3. Backend: WebSocket Integration with Analysis

- [ ] 3.1 Queue chunks for analysis as they arrive via WebSocket
  - Use threading/threading.Thread for async processing
  - Process chunks sequentially (maintain order)
  - Don't block WebSocket receive on analysis
- [ ] 3.2 Send analysis results back to client via WebSocket
  - Format results as JSON: `{notes: [...], chord: "...", confidence: ..., timestamp: ...}`
  - Send deltas only (new or changed detections)
  - Handle network errors gracefully
- [ ] 3.3 Implement cancellation mechanism
  - Client can send "cancel" message to stop session
  - Server stops accepting chunks and stops analysis
  - Clean up session data

## 4. Frontend: Improvisation/Practice Mode Page

- [ ] 4.1 Create `templates/improvise.html` page
  - Layout: microphone controls (top), chord display (center), timeline (side)
  - Add styles (extend `static/css/style.css`)
  - Responsive design for desktop/tablet
- [ ] 4.2 Add "Improvise" button/link to main navigation
  - Link from `templates/base.html` navigation
  - Route: `/improvise` GET endpoint in `app.py`
- [ ] 4.3 Implement browser microphone capture with MediaRecorder
  - Request microphone permission on button click
  - Start MediaRecorder on permission grant
  - Capture audio in 1-second chunks
  - Encode to MP3 or Opus codec
- [ ] 4.4 Implement WebSocket client connection
  - Connect to `/ws/improvise` on record start
  - Send audio chunks as they're captured
  - Listen for analysis results on connection
  - Handle connection errors/reconnection

## 5. Frontend: Real-Time Results Display

- [ ] 5.1 Display current chord in large, prominent text
  - Center of page, large font size (48px+)
  - Update within 1-2 seconds of new detection
  - Show chord name and quality (e.g., "C Major 7th")
- [ ] 5.2 Display current notes being played
  - Below chord, smaller text
  - Show as space-separated list (e.g., "C E G B")
  - Color-code by role: chord tone (green), tension (yellow), avoid (red)
- [ ] 5.3 Create chord timeline/history view
  - Left/side panel showing all detected chords chronologically
  - Format: `[HH:MM:SS - HH:MM:SS] Chord Name (duration)`
  - Highlight currently-playing chord
  - Auto-scroll to keep current chord visible
- [ ] 5.4 Add confidence indicator
  - Show confidence % next to chord (e.g., "C Major (95%)")
  - Or use visual indicator (opacity, badge color)
  - Update as confidence increases with more audio
- [ ] 5.5 Implement session timer display
  - Countdown timer: `MM:SS` format
  - Large, visible (top-right or prominent location)
  - Turn red as user approaches 10-minute limit

## 6. Frontend: Session Controls

- [ ] 6.1 Add "Start Recording" button
  - Requests microphone permission
  - Initiates WebSocket connection
  - Starts MediaRecorder and timer
- [ ] 6.2 Add "Stop Recording" button (visible while recording)
  - Stops microphone capture
  - Closes WebSocket connection
  - Shows "Export" and "Discard" buttons
- [ ] 6.3 Implement "Discard" button
  - Clears all session data (audio and analysis results)
  - Returns to idle state with "Start Recording" button
- [ ] 6.4 Add "Export to HTML" button
  - Disabled if session < 30 seconds
  - Click triggers HTML export download

## 7. Frontend: Error Handling & User Feedback

- [ ] 7.1 Handle microphone permission denied
  - Show error: "Microphone access required to start improvisation analysis"
  - Keep "Start Recording" button available
- [ ] 7.2 Handle microphone unavailable
  - Show error: "Microphone not available. Check your device settings."
  - Disable "Start Recording" button
- [ ] 7.3 Handle WebSocket connection errors
  - Show notification if connection drops during session
  - Offer to reconnect or discard session
- [ ] 7.4 Handle "Listening..." state during silence
  - Display placeholder during quiet periods
  - Don't show stale chord detections
- [ ] 7.5 Add loading indicator
  - Show spinner while awaiting first chord detection
  - Remove after first result arrives

## 8. Backend: HTML Export for Sessions

- [ ] 8.1 Create session export function in `export.py`
  - Input: session data (chord timeline, metadata)
  - Output: standalone HTML file
  - Reuse existing HTML styling/structure from track exports
- [ ] 8.2 Generate HTML with chord timeline
  - Table or list format showing all detected chords with timestamps
  - Color coding (chord tones, extensions, etc.)
  - Chronological order
- [ ] 8.3 Add session metadata to HTML
  - Session start date/time
  - Total duration recorded
  - Instrument/context (if user provided)
  - Confidence summary
- [ ] 8.4 Ensure HTML is fully standalone
  - All CSS inline (no external stylesheets)
  - All JavaScript inline (no external scripts)
  - No CDN dependencies
  - Works offline

## 9. Backend: Export Route & Download

- [ ] 9.1 Create export endpoint in `app.py`
  - POST `/sessions/<session_id>/export` endpoint
  - Calls session export function
  - Returns HTML file as download
  - Sets proper Content-Type and Content-Disposition headers
- [ ] 9.2 Clean up session data after export
  - Delete session from memory after export
  - Prevent re-export of same session
  - Handle race conditions (simultaneous exports)

## 10. Testing

- [ ] 10.1 Unit test: WebSocket connection and chunk receiving
  - Mock WebSocket client
  - Verify chunks are received and queued
- [ ] 10.2 Unit test: Audio chunk analysis
  - Test `stream_analyze()` with sample audio
  - Verify chord detection works on short chunks
  - Verify rolling window refinement logic
- [ ] 10.3 Unit test: Session management
  - Create/destroy sessions
  - Verify timeout logic
  - Verify memory cleanup
- [ ] 10.4 Unit test: HTML export generation
  - Export session data to HTML
  - Verify all metadata is included
  - Verify HTML is valid and standalone
- [ ] 10.5 Integration test: Full improvisation workflow
  - Start session → send audio chunks → receive detections → stop → export
  - Verify results match expected chord timeline
  - Test with real microphone input if possible
- [ ] 10.6 Frontend test: Microphone capture and WebSocket
  - Mock MediaRecorder
  - Verify chunks are sent correctly
  - Test error handling (permission denied, unavailable)
- [ ] 10.7 Frontend test: Results display updates
  - Verify chord display updates when new detection arrives
  - Verify timeline updates correctly
  - Test confidence and note display

## 11. Documentation & Deployment

- [ ] 11.1 Update README.md
  - Add "Improvisation/Practice Mode" section
  - Explain microphone capture flow
  - Note that sessions are ephemeral
  - Mention HTML export feature
- [ ] 11.2 Update CLAUDE.md with new feature
  - Add live-improvisation-analysis to feature list
  - Document architecture decisions
- [ ] 11.3 Test full workflow end-to-end
  - Improvise for 5-10 minutes
  - Verify chord detection accuracy
  - Export and review HTML
  - Test on different browsers (Chrome, Firefox, Safari)
- [ ] 11.4 Deploy to staging
  - Test with real network conditions
  - Monitor memory usage during sessions
  - Verify WebSocket stability
- [ ] 11.5 Create user guide
  - Screenshots of improvisation mode
  - How to start/stop session
  - Tips for best chord detection (clear audio, distinct notes)
  - How to export and review results
