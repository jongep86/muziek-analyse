## ADDED Requirements

### Requirement: Display detected chords and notes in real-time
The system SHALL show detected notes and chords as they arrive from the analysis backend, with clear visual indication of what the user is currently playing.

#### Scenario: Currently playing chord is prominently displayed
- **WHEN** chord analysis completes for the current audio chunk
- **THEN** the detected chord is displayed in large text (e.g., "C Major 7th")
- **THEN** the display updates within 1-2 seconds of new chunk arrival

#### Scenario: Current notes are shown
- **WHEN** individual notes are detected
- **THEN** they are displayed below or alongside the current chord (e.g., "C, E, G, B")
- **THEN** notes are color-coded by role: chord tone (green), extension/tension (yellow), avoid note (red)

#### Scenario: Timeline of detected chords appears during session
- **WHEN** recording is active and chords are detected
- **THEN** a timeline or list on the left/side panel shows all previously detected chords with timestamps
- **THEN** each chord in the timeline shows elapsed time and duration held (e.g., "0:00-0:05: C Major 7th")

#### Scenario: Current position is highlighted in timeline
- **WHEN** new chords are detected
- **THEN** the most recent chord in the timeline is highlighted or scrolled into view
- **THEN** user can see their progression through the improvisation

#### Scenario: Confidence is visually indicated
- **WHEN** chord detection has low confidence (e.g., <70%)
- **THEN** the chord display includes a confidence indicator (e.g., opacity, badge, percentage)
- **THEN** as more audio arrives, the display updates and confidence increases

#### Scenario: Empty/silence periods are handled
- **WHEN** no clear notes are detected (silence, noise, or very low signal)
- **THEN** the display shows "Listening..." or similar placeholder
- **THEN** the timeline may mark this as a pause or skip this period
