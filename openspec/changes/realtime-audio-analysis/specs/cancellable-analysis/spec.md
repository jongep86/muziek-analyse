## ADDED Requirements

### Requirement: Cancel analysis mid-operation
The system SHALL allow users to stop an ongoing analysis at any time without data loss or hanging processes.

#### Scenario: User cancels during upload
- **WHEN** user clicks "Cancel" button while file is uploading
- **THEN** the upload stops, partial results are saved, and no further processing occurs

#### Scenario: User cancels during analysis
- **WHEN** user clicks "Cancel" button while analysis is in progress (after upload completes)
- **THEN** the system completes current chunk processing, saves partial results, and stops

#### Scenario: Cancel button is disabled when appropriate
- **WHEN** analysis has already completed
- **THEN** the Cancel button is disabled (greyed out) since there's nothing to cancel

### Requirement: Clean shutdown without resource leaks
The system SHALL ensure that cancelled analysis doesn't leave orphaned processes, temporary files, or database locks.

#### Scenario: Worker thread stops gracefully
- **WHEN** analysis is cancelled
- **THEN** the worker thread checks the cancellation flag between chunks and exits cleanly

#### Scenario: Database is left in consistent state
- **WHEN** analysis is cancelled mid-chunk
- **THEN** the database reflects either the last completed chunk or rolls back the partial chunk, never a corrupted state
