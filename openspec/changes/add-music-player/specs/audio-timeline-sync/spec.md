## ADDED Requirements

### Requirement: Highlight active chord during playback
The system SHALL visually indicate which chord is currently playing by highlighting the corresponding block in the timeline.

#### Scenario: Audio playback advances to a new chord
- **WHEN** the playback position enters a new chord's time range (start <= currentTime < end)
- **THEN** the timeline block for that chord is highlighted with a distinct style (e.g., bright border, background color change)

#### Scenario: Previous chord is unhighlighted
- **WHEN** playback exits a chord's time range
- **THEN** the previous chord's highlight is removed

#### Scenario: Playback at section boundary
- **WHEN** the playback position is exactly at the start of a chord
- **THEN** that chord's block is immediately highlighted without delay

### Requirement: Scroll timeline into view
The system SHALL automatically scroll the timeline so the active chord remains visible to the user.

#### Scenario: Active chord is off-screen
- **WHEN** the highlighted chord is not visible in the current viewport
- **THEN** the timeline automatically scrolls to bring the active chord into view

#### Scenario: User manually scrolls timeline
- **WHEN** user scrolls the timeline while audio is playing
- **THEN** automatic scrolling is temporarily suspended but highlighting continues; when the user stops scrolling, automatic scroll resumes if needed

### Requirement: Update section highlighting
The system SHALL highlight the active section alongside chord highlighting.

#### Scenario: Playback enters a new section
- **WHEN** playback position enters a section's time range
- **THEN** the section container is visually highlighted (e.g., background color, border)
