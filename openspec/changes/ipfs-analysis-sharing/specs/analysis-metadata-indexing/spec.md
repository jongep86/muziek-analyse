## ADDED Requirements

### Requirement: Index shared analyses locally
The system SHALL build a searchable index of shared analyses to enable fast discovery without querying IPFS for every search.

#### Scenario: New analysis is indexed when shared
- **WHEN** an analysis is published to IPFS
- **THEN** its metadata (artist, title, key, BPM, timestamp) is added to the local search index

#### Scenario: Index supports full-text search
- **WHEN** user searches for a track
- **THEN** the system returns results matching artist name, song title, or key using full-text search

#### Scenario: Index is persistent
- **WHEN** the app is closed and reopened
- **THEN** the search index is restored and ready to use without re-indexing

### Requirement: Allow users to build their own index
The system SHALL allow power users to expand the local index by pinning additional shared analyses.

#### Scenario: User pins analysis from discovery
- **WHEN** user clicks "Pin" on a shared analysis
- **THEN** the analysis metadata is added to their local index for future searching

#### Scenario: Pinned analyses are cached
- **WHEN** analyses are pinned
- **THEN** their data is stored locally so they can be accessed without IPFS if offline
