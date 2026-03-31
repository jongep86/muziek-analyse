## ADDED Requirements

### Requirement: Search shared analyses
The system SHALL allow users to search and discover analyses shared by others on IPFS.

#### Scenario: User searches by track name
- **WHEN** user enters a song title in the discovery search box
- **THEN** results show matching shared analyses from the local index with artist, key, tempo, and uploader

#### Scenario: User filters by key or tempo
- **WHEN** user filters search results by key (e.g., "Em") or tempo range (e.g., 80-120 BPM)
- **THEN** results are narrowed to matching criteria

#### Scenario: User browses all shared analyses
- **WHEN** user visits the discovery page
- **THEN** a paginated list of all indexed analyses is shown, most recently shared first

### Requirement: Display analysis details
The system SHALL show metadata and preview of each shared analysis without requiring download.

#### Scenario: User views shared analysis preview
- **WHEN** user clicks on a search result
- **THEN** a preview shows the analysis data (chords timeline, key, patterns, tips) in read-only mode

#### Scenario: User sees uploader and timestamp
- **WHEN** viewing a shared analysis
- **THEN** metadata shows who shared it and when it was published
