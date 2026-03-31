## ADDED Requirements

### Requirement: Play audio from file
The system SHALL provide an audio player that plays the audio file associated with the current track using standard playback controls.

#### Scenario: User initiates playback
- **WHEN** user clicks the play button on the audio player
- **THEN** audio starts playing from the current position

#### Scenario: User pauses playback
- **WHEN** user clicks the pause button during playback
- **THEN** audio pauses at the current position and can be resumed

#### Scenario: User adjusts playback volume
- **WHEN** user moves the volume slider
- **THEN** audio playback volume changes accordingly (0-100%)

#### Scenario: User seeks to a new position
- **WHEN** user clicks on the timeline or drags the seek slider to a new time
- **THEN** audio jumps to that position and resumes playback (or paused state if paused)

### Requirement: Display current time and duration
The system SHALL display the current playback time and total duration of the audio track.

#### Scenario: Time updates during playback
- **WHEN** audio is playing
- **THEN** the current time display updates continuously (at least every 100ms)

#### Scenario: Duration is displayed on load
- **WHEN** a track detail page loads
- **THEN** the total duration is shown (e.g., "3:45" for 3 minutes 45 seconds)

### Requirement: Handle missing audio files
The system SHALL gracefully handle cases where the audio file is not available.

#### Scenario: File is missing
- **WHEN** the audio file path does not exist or is inaccessible
- **THEN** the player shows a disabled state with a message "Audio file not found" and no controls are functional
