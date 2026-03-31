## ADDED Requirements

### Requirement: Publish analysis to IPFS
The system SHALL publish an analysis to IPFS and return a persistent content hash that can be shared.

#### Scenario: User publishes an analysis
- **WHEN** user clicks "Share" button on track detail page
- **THEN** the analysis (including metadata) is published to IPFS and a content hash is generated

#### Scenario: Content hash is stored locally
- **WHEN** analysis is published to IPFS
- **THEN** the content hash is saved in the local database alongside `is_shared: true` and publication timestamp

#### Scenario: Share link is provided to user
- **WHEN** analysis is published
- **THEN** user is shown a shareable IPFS link (e.g., `ipfs://QmXxxx...` or gateway URL) that they can send to others

### Requirement: Include metadata with analysis
The system SHALL wrap the analysis with searchable metadata before publishing to IPFS.

#### Scenario: Metadata is captured
- **WHEN** an analysis is published
- **THEN** the IPFS content includes artist, title, key, BPM, uploader, and timestamp alongside the full analysis data

#### Scenario: Published content is immutable
- **WHEN** analysis is published to IPFS
- **THEN** the content becomes immutable; the same analysis always produces the same content hash
