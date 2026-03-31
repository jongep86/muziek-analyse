## Why

Large audio files (>50MB) take significant time to upload and process sequentially. By analyzing audio chunks as they arrive, users can see partial results (key, BPM, initial chords) while upload continues, providing faster feedback and allowing early cancellation if needed.

## What Changes

- Detect audio format and key details from the first chunk without waiting for full file
- Extract initial key/BPM from the first 30-60 seconds of audio
- Stream chunks to the analysis pipeline incrementally instead of processing entire file at once
- Show "partial analysis" UI state with available data while upload/analysis continues
- Allow users to cancel analysis mid-upload
- Persist intermediate results so users can view progress without waiting for completion

## Capabilities

### New Capabilities
- `chunk-based-analysis`: Process audio in chunks as they arrive rather than waiting for full file download/upload
- `partial-results-display`: Show incomplete but valid analysis results (key, BPM, partial chords) while full analysis is in progress
- `streaming-upload-analysis`: Detect audio format and extract basic metadata from stream headers before full transfer
- `cancellable-analysis`: Allow users to stop an ongoing analysis at any time without data loss
- `analysis-progress-tracking`: Display real-time progress of multi-chunk analysis with ETA

### Modified Capabilities
- `track-analysis-pipeline`: Change from batch/offline analysis to incremental/streaming analysis that can yield partial results

## Impact

- **Backend**: Add streaming analysis pipeline in `tasks.py`, modify `analyse.py` to support chunk-based detection
- **Frontend**: Add progress indicators and partial results display in `templates/index.html` and `templates/track_detail.html`
- **Database**: Store intermediate analysis states and timestamps for partial results
- **Dependencies**: May require additional libraries for chunk-based audio processing (librosa supports this)
- **Performance**: First results appear within seconds instead of minutes for large files
