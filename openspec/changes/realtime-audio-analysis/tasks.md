## 1. Chunk-Based File Reading

- [ ] 1.1 Add chunk reading utility function in `analyse.py`
  - Accepts file path and chunk size (default 1-2 MB)
  - Yields chunks sequentially
  - Supports both file paths and file-like objects (for streams)
- [ ] 1.2 Create `ChunkProcessor` class in `analyse.py`
  - Initializes with audio file/stream
  - Detects format from first chunk headers
  - Accumulates audio data across chunks for librosa processing

## 2. Fast Pass (Preliminary Analysis)

- [ ] 2.1 Implement fast key/BPM detection in `analyse.py`
  - Function `analyse_key_bpm_fast(audio_chunk, sr)` extracts key and BPM from first 30-60 seconds
  - Uses Krumhansl-Schmuckler for key detection (already in codebase)
  - Returns key, confidence, and BPM estimate
- [ ] 2.2 Store preliminary results in database
  - Update `models.py` to support `_meta.status: 'partial'` in analysis_data
  - Timestamp when preliminary results are saved
  - Mark completion percentage (e.g., 20% of file processed)

## 3. Chunk Processing Pipeline

- [ ] 3.1 Modify `tasks.py` to support chunk-based analysis
  - Add `enqueue_streaming` function for stream uploads
  - Worker checks for cancellation flag between chunks
  - Aggregates results from multiple chunks
- [ ] 3.2 Add intermediate result persistence
  - Save after every N chunks (e.g., every 5 chunks) instead of after each chunk
  - Prevents database churn
  - Maintains consistency by checking for cancellation before write

## 4. Cancellation Support

- [ ] 4.1 Add cancellation flag to analysis state in `tasks.py`
  - Set flag when user clicks "Cancel"
  - Worker thread checks flag between chunk processing
  - Rolls back incomplete chunk, saves last complete state
- [ ] 4.2 Implement cancel endpoint in `app.py`
  - POST `/tracks/<id>/cancel` endpoint
  - Sets cancellation flag in background task

## 5. Frontend Progress Tracking

- [ ] 5.1 Update `index.html` active tracks banner
  - Show progress bar with percentage complete
  - Display current step (e.g., "Downloading...", "Detecting key...", "Analyzing chords...")
  - Show estimated time remaining
- [ ] 5.2 Add progress polling in JavaScript
  - Poll `/analyse/status/<track_id>` more frequently during analysis (every 500ms instead of 1000ms)
  - Update progress bar and step text in real-time
  - Show cancel button during analysis
- [ ] 5.3 Implement cancel button handler
  - POST to `/tracks/<id>/cancel` when clicked
  - Disable button after click
  - Show "Cancelled, saving results..." message

## 6. Partial Results Display

- [ ] 6.1 Update `track_detail.html` to show partial status
  - Add "Preliminary Results" badge if `_meta.status == 'partial'`
  - Show completion percentage and timestamp
  - Disable export options if analysis is incomplete
- [ ] 6.2 Handle incomplete sections gracefully
  - Pattern section: show "Analysis in progress..." if not available
  - Melody section: show "Detected from first segment" if partial
  - Sections timeline: show only detected sections with "More to come..." indicator
- [ ] 6.3 Add refresh button to re-load partial results
  - Allow user to see updated results without page reload
  - Updates via AJAX call to `/tracks/<id>` endpoint

## 7. Format Detection

- [ ] 7.1 Add audio format detection utility
  - Use librosa or audioread to detect format from stream headers
  - Extract sample rate, bit depth, duration estimate from headers
  - Validate format is supported (MP3, WAV, FLAC, OGG, etc.)
- [ ] 7.2 Add format validation at chunk start
  - Reject unsupported formats before accepting full upload
  - Return error to user with supported formats list

## 8. Database Schema Updates

- [ ] 8.1 Add `_meta` field to analysis_data JSON schema
  - `_meta.status`: 'partial' | 'complete' | 'error'
  - `_meta.completion_pct`: integer 0-100
  - `_meta.timestamp`: ISO timestamp of last update
  - `_meta.chunks_processed`: number of chunks analyzed
- [ ] 8.2 Add cancellation support to models
  - Track `is_cancelled` flag in analysis state
  - Update models to check this flag before writing

## 9. Testing & Integration

- [ ] 9.1 Test fast key/BPM detection
  - Upload a large file and verify preliminary results appear within 10 seconds
  - Verify results are accurate compared to full analysis
  - Test with different file formats (MP3, WAV, FLAC)
- [ ] 9.2 Test chunk processing
  - Upload files in various sizes (10MB, 100MB, 1GB)
  - Verify chunks are processed in correct order
  - Check no data loss between chunks
- [ ] 9.3 Test cancellation
  - Cancel during upload
  - Cancel during fast pass
  - Cancel during full analysis
  - Verify partial results are saved in all cases
- [ ] 9.4 Test progress display
  - Verify progress bar updates smoothly
  - Check ETA is reasonable
  - Verify step indicator changes appropriately
  - Test on both desktop and mobile
- [ ] 9.5 Test concurrent uploads
  - Upload multiple files simultaneously
  - Verify queue order is maintained
  - Check database doesn't get corrupted

## 10. Documentation & Deployment

- [ ] 10.1 Update README
  - Document streaming analysis feature
  - Explain preliminary vs complete results
  - Note supported file formats and size limits
- [ ] 10.2 Update CLAUDE.md
  - Add streaming analysis to features list
  - Note chunk size and fast-pass timeout values
- [ ] 10.3 Commit and test on staging
  - Deploy to test environment
  - Verify with real users that UX is clear
  - Gather feedback on progress messaging
- [ ] 10.4 Deploy to production
  - Monitor for performance regressions
  - Check error logs for new edge cases
