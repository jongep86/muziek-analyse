## ADDED Requirements

### Requirement: Capture live microphone audio
The system SHALL capture audio from the user's microphone and stream it to the server for analysis.

#### Scenario: User starts improvisation session
- **WHEN** user navigates to the improvisation/practice mode page
- **THEN** a "Start Recording" button is displayed with microphone icon

#### Scenario: User grants microphone permission
- **WHEN** user clicks "Start Recording"
- **THEN** the browser requests microphone permission via standard permission dialog
- **THEN** upon grant, audio capture begins

#### Scenario: Audio is streamed in chunks
- **WHEN** microphone is actively recording
- **THEN** audio is captured in 1-second chunks and streamed to server via WebSocket
- **THEN** each chunk is encoded in a standard codec (Opus or MP3)

#### Scenario: User denies microphone permission
- **WHEN** user denies microphone access in the permission dialog
- **THEN** an error message displays: "Microphone access required to start improvisation analysis"
- **THEN** the "Start Recording" button remains available for retry

#### Scenario: Microphone is unavailable
- **WHEN** the browser cannot access a microphone (no hardware or other app has exclusive access)
- **THEN** an error message displays: "Microphone not available. Check your device settings."
- **THEN** the "Start Recording" button is disabled until page reload
