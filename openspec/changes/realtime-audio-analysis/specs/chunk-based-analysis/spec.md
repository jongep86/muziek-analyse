## ADDED Requirements

### Requirement: Process audio in chunks
The system SHALL read audio files in chunks and process each chunk incrementally rather than loading the entire file at once.

#### Scenario: File is read in chunks
- **WHEN** a file upload begins
- **THEN** the system reads the file in 1-2 MB chunks and processes each chunk immediately without waiting for subsequent chunks

#### Scenario: Quick initial results
- **WHEN** the first chunk is processed
- **THEN** preliminary key and BPM results are available within 5-10 seconds, before the full file is uploaded

#### Scenario: Results refine with more chunks
- **WHEN** additional chunks are processed
- **THEN** analysis results are updated/refined with new data (e.g., BPM becomes more accurate, chords become more complete)

### Requirement: Support streaming input
The system SHALL accept audio input from both file uploads and streaming sources (YouTube, URL streams).

#### Scenario: File upload streaming
- **WHEN** user uploads a large audio file
- **THEN** the system chunks the incoming upload and begins analysis before upload completes

#### Scenario: YouTube download streaming
- **WHEN** user imports from YouTube
- **THEN** the system chunks the downloaded audio and begins analysis during download
