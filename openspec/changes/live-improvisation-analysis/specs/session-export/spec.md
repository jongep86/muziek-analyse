## ADDED Requirements

### Requirement: Export improvisation session results to HTML
The system SHALL allow users to export the results of an improvisation session (timeline of detected chords/notes) to a standalone HTML file.

#### Scenario: Export button appears after session ends
- **WHEN** user stops the recording (manually or by timeout)
- **THEN** an "Export to HTML" button is displayed alongside "Discard"
- **THEN** the button is disabled if session is shorter than 30 seconds

#### Scenario: HTML export includes session metadata
- **WHEN** user clicks "Export to HTML"
- **THEN** a file dialog appears to choose save location
- **THEN** the downloaded HTML includes:
  - Session start date and time
  - Total duration recorded
  - Instrument/context (optional metadata if user fills it)

#### Scenario: HTML contains full chord timeline
- **WHEN** export is generated
- **THEN** the HTML displays a complete timeline of detected chords with timestamps
- **THEN** each chord entry shows:
  - Start and end time
  - Detected chord name
  - Detected notes
  - Confidence level (if available)

#### Scenario: HTML is standalone and self-contained
- **WHEN** the exported HTML file is opened
- **THEN** it displays correctly without requiring internet connection or external resources
- **THEN** styling and interactive elements (if any) are embedded as inline CSS/JavaScript
- **THEN** no external CDN dependencies are used

#### Scenario: User can review chord progression
- **WHEN** exported HTML is opened
- **THEN** user can scroll through the chord timeline
- **THEN** chords are organized chronologically
- **THEN** user can visually see the progression of what they played

#### Scenario: Export format is similar to track analysis
- **WHEN** HTML is exported
- **THEN** the design and layout are consistent with existing track analysis HTML exports
- **THEN** similar color coding and visual hierarchy are used
