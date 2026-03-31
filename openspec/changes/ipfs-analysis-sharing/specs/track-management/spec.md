## MODIFIED Requirements

### Requirement: Manage tracks
The system SHALL allow users to create, edit, delete, and organize their tracks.

**Updated behavior**: Track management now supports importing shared analyses from IPFS alongside local uploads.

#### Scenario: User imports from IPFS
- **WHEN** user accesses an "Import from IPFS" or "Discover" interface
- **THEN** they can search for, preview, and import shared analyses into their local database

#### Scenario: Imported analysis appears in track list
- **WHEN** an analysis is imported from IPFS
- **THEN** it appears in the main track list and can be edited or re-shared locally

#### Scenario: Version history for re-shared analyses
- **WHEN** user imports an analysis they've already analyzed locally
- **THEN** both versions are stored and user can switch between them or merge insights

#### Scenario: Track list shows share status
- **WHEN** viewing the main tracks list
- **THEN** each track shows a small indicator (icon or badge) if it's shared/public or private

### Requirement: Sync analyses
The system SHALL support importing versions of the same analysis from different sources.

#### Scenario: Compare local and imported analysis
- **WHEN** user has both a local analysis and an imported shared version
- **THEN** track detail page allows viewing side-by-side or selecting which version to display

#### Scenario: Merge or fork analyses
- **WHEN** viewing multiple versions of the same analysis
- **THEN** user can create a new analysis incorporating insights from both versions
