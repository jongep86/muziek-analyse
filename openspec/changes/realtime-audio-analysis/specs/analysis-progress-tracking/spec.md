## ADDED Requirements

### Requirement: Display real-time progress
The system SHALL show the user how much of the file has been processed and estimated time remaining.

#### Scenario: Progress bar updates
- **WHEN** analysis is in progress
- **THEN** a progress bar shows the percentage of the file that has been processed (0-100%)

#### Scenario: Estimated time is displayed
- **WHEN** analysis is running and enough chunks have been processed to estimate speed
- **THEN** an estimated time remaining (e.g., "~2 minutes remaining") is shown

#### Scenario: Processing speed indicator
- **WHEN** user hovers over or clicks the progress display
- **THEN** current processing speed is shown (e.g., "Processing: 2.5 MB/s")

### Requirement: Show current step of analysis
The system SHALL indicate which analysis phase is currently running (upload → detect format → extract key → detect chords, etc.).

#### Scenario: Step indicator updates
- **WHEN** analysis transitions between phases
- **THEN** the current step is displayed (e.g., "Detecting chords..." → "Analyzing patterns...")

#### Scenario: No step indicator for completed file
- **WHEN** analysis is complete
- **THEN** the progress display changes to show "Analysis complete" with a completion timestamp
