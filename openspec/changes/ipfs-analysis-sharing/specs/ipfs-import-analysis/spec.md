## ADDED Requirements

### Requirement: Import shared analysis from IPFS
The system SHALL allow users to download and import analyses from IPFS using content hash or discovery interface.

#### Scenario: User imports via content hash
- **WHEN** user enters or pastes an IPFS content hash (e.g., `QmXxxx...`)
- **THEN** the system fetches the analysis from IPFS and imports it as a local track

#### Scenario: User imports from discovery
- **WHEN** user clicks "Import" on a shared analysis preview
- **THEN** the analysis is downloaded from IPFS and added to their local database

#### Scenario: Imported analysis is marked as shared
- **WHEN** analysis is imported from IPFS
- **THEN** it's saved locally with `is_shared: true` and the original content hash recorded

### Requirement: Handle import conflicts
The system SHALL gracefully handle cases where an analysis for the same track already exists locally.

#### Scenario: Track already analyzed
- **WHEN** user imports an analysis for a track they've already analyzed
- **THEN** system shows a dialog: "You already have an analysis for this track. Import as new version or compare?"

#### Scenario: User creates version
- **WHEN** user chooses to create a new version
- **THEN** both analyses are stored (original + imported) and user can switch between them
