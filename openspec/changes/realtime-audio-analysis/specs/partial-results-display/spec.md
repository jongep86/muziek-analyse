## ADDED Requirements

### Requirement: Display partial analysis results
The system SHALL display incomplete but valid analysis results while the full analysis is still in progress.

#### Scenario: Preliminary key is shown
- **WHEN** the first chunk completes analysis
- **THEN** the detected key and confidence are displayed with a "Preliminary" label

#### Scenario: BPM updates as more data arrives
- **WHEN** additional chunks are processed
- **THEN** the BPM field updates with refined estimate and remains visible

#### Scenario: Partial chord timeline appears
- **WHEN** the first 30-60 seconds of chords are detected
- **THEN** a partial chord timeline is shown with a progress indicator showing what percentage is complete

### Requirement: Label results as partial or complete
The system SHALL clearly indicate whether displayed results are preliminary or final.

#### Scenario: Partial results are labeled
- **WHEN** analysis is in progress
- **THEN** all displayed results show a badge or label like "Preliminary" or "In Progress: 45%"

#### Scenario: Results update to "Complete" when done
- **WHEN** full analysis finishes
- **THEN** the "Preliminary" label is removed and all results reflect the complete analysis

### Requirement: Handle incomplete data gracefully
The system SHALL display available data without crashing or showing errors for missing sections.

#### Scenario: Patterns not yet available
- **WHEN** full analysis is still running but patterns haven't been detected yet
- **THEN** the patterns section shows "Analysis in progress..." instead of empty or error state
