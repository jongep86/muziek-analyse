## Context

Currently, analysis runs as a single batch job after the full file is uploaded. For large files (>100MB), this can take 5+ minutes before any results are visible. Streaming analysis would extract key, BPM, and initial chords from the first 30-60 seconds while more data arrives, giving users faster feedback.

The project uses Flask + threading for background tasks, and librosa for audio analysis. Both support chunk-based processing.

## Goals / Non-Goals

**Goals:**
- Display initial key/BPM within 10 seconds of upload starting (from first chunk)
- Show partial chord analysis while full analysis continues
- Allow cancellation at any point during analysis
- Maintain data integrity (no partial/corrupted results saved)
- Support both uploaded files and YouTube imports

**Non-Goals:**
- Real-time visualization (waveform, frequency analysis) during playback
- Live streaming from radio or continuous sources
- Distributed processing across multiple servers
- Streaming to clients (results still stored on server)

## Decisions

### 1. Two-Pass Analysis Strategy
**Decision:** First pass extracts key/BPM from first 30-60 seconds, second pass completes full analysis.

**Rationale:** Fast initial feedback without over-complicating the architecture. Users see results quickly, can inspect or cancel before full analysis runs.

**Alternatives:**
- Streaming all features incrementally (more complex, marginal benefit)
- Chunked processing throughout (would require refactoring entire analysis pipeline)

### 2. File Chunking Approach
**Decision:** Read audio file in 1-2 MB chunks, process each chunk immediately.

**Rationale:** Balance between I/O efficiency and responsiveness. Small chunks = fast first results; larger chunks = less overhead.

**Implementation:**
- Read chunks sequentially from file or stream
- Pass each chunk to librosa for analysis
- Aggregate results (key is most stable, BPM can vary, chords refine)

### 3. Partial Results Storage
**Decision:** Store partial analysis with timestamp and completion percentage in database.

**Rationale:** Allows users to see progress without waiting. If analysis is cancelled or fails, partial results still visible.

**Schema:**
- `analysis_data` JSON now includes `_meta: {status: 'partial'|'complete', completion_pct, timestamp, chunks_processed}`

### 4. UI State Management
**Decision:** Track analysis state in frontend (pending → uploading → analyzing → partial → complete → error).

**Rationale:** Clear progress messaging and allows UI to show different information for each state.

### 5. Cancellation Mechanism
**Decision:** Set a flag in the database that worker thread checks between chunks.

**Rationale:** Clean shutdown without hanging processes or corrupted data.

## Risks / Trade-offs

**[Partial results inconsistency]** → Key detected from first 30s might differ from full file key. *Mitigation:* Label partial results as "preliminary" and update as more data arrives.

**[Large file memory usage]** → Chunked reading still requires buffering in memory. *Mitigation:* Keep chunk size small (1-2 MB) and process immediately.

**[UI complexity]** → Multiple progress states and partial data types complicate frontend logic. *Mitigation:* Use incremental UI updates (React-like patterns, no full re-render).

**[Database churn]** → Frequent updates to partial results during analysis. *Mitigation:* Batch updates (every 5 chunks) instead of every chunk.

## Migration Plan

1. **Phase 1 (Non-breaking):**
   - Add `_meta` field to analysis JSON (ignored by existing UI)
   - Implement fast key/BPM detection
   - Queue both "fast pass" and "full pass" jobs

2. **Phase 2 (UI Update):**
   - Detect partial state in frontend
   - Show progress bar + preliminary results
   - Allow cancellation

3. **Phase 3 (Optimization):**
   - Batch database updates
   - Optimize chunk sizes for different file types

## Open Questions

1. Should partial results be exported to HTML/Markdown or only viewed in web UI?
2. How long to keep partial results if user cancels (cleanup strategy)?
3. Should first 30-60s always be analyzed or should it be smarter based on file size?
