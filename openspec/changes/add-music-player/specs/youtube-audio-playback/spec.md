## ADDED Requirements

### Requirement: Play YouTube-sourced audio
The system SHALL support playback of audio files that were downloaded from YouTube and stored locally.

#### Scenario: YouTube track analysis is complete
- **WHEN** a YouTube import has finished downloading and analysis is done
- **THEN** the audio player is available with the same controls as regular uploaded tracks

#### Scenario: User plays YouTube-sourced track
- **WHEN** user clicks play on a track with source='youtube'
- **THEN** the locally downloaded audio file is played (no re-download or streaming from YouTube)

### Requirement: Handle YouTube tracks with missing downloads
The system SHALL gracefully degrade if a YouTube track's downloaded file is missing.

#### Scenario: Downloaded file was deleted
- **WHEN** a YouTube track's audio file has been deleted from disk
- **THEN** the player shows a disabled state with message "Audio file not found" (same as regular missing files)

#### Scenario: Download failed previously
- **WHEN** a YouTube import task failed during download
- **THEN** the player is disabled and a message suggests re-importing or checking the audio file
