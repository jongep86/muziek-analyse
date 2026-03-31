## ADDED Requirements

### Requirement: Manage improvisation sessions with time limit
The system SHALL enforce a 5-10 minute time limit on improvisation sessions and provide controls to start, stop, and manage sessions.

#### Scenario: Session timer displays during recording
- **WHEN** audio capture begins
- **THEN** a session timer displays on screen showing elapsed time (MM:SS format)
- **THEN** the timer counts up from 0:00 toward the 10-minute limit

#### Scenario: Session auto-stops at 10 minutes
- **WHEN** elapsed time reaches 10 minutes
- **THEN** audio capture automatically stops
- **THEN** a message displays: "Session limit reached. Click Export to save results."
- **THEN** the user can no longer extend the session (time limit is hard stop)

#### Scenario: User can manually stop before timeout
- **WHEN** a session is active and user clicks "Stop Recording"
- **THEN** audio capture stops immediately
- **THEN** the elapsed time is frozen
- **THEN** user is presented with options: "Export" or "Discard"

#### Scenario: User can discard session
- **WHEN** user clicks "Discard" after stopping a session
- **THEN** all session data (audio and analysis) is deleted
- **THEN** the interface returns to the idle state with "Start Recording" button ready

#### Scenario: Session persists only while active
- **WHEN** a session ends (by timeout, user stop, or discard)
- **THEN** the session data is removed from memory
- **THEN** if user closes the browser tab or refreshes during a session, the session is lost (no recovery)

#### Scenario: Minimum session duration before export
- **WHEN** user has recorded for less than 30 seconds
- **THEN** the "Export" button is disabled or shows message: "Record at least 30 seconds before exporting"
