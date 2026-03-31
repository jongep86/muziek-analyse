## MODIFIED Requirements

### Requirement: Display track detail information
The system SHALL show all analysis data and metadata for a track on the detail page.

**Updated behavior**: The detail page now includes share/unshare controls and displays public/private status.

#### Scenario: Share button appears on detail page
- **WHEN** user views track detail for a private analysis
- **THEN** a "Share to IPFS" button is visible

#### Scenario: Unshare button appears for shared tracks
- **WHEN** user views track detail for a shared/published analysis
- **THEN** an "Unshare" button is visible instead of "Share"

#### Scenario: Public status is displayed
- **WHEN** viewing track detail
- **THEN** a badge shows "Shared" with the IPFS content hash (or "Private" if not shared)

#### Scenario: Copy share link
- **WHEN** user clicks the IPFS content hash or a "Copy Link" button
- **THEN** the shareable IPFS URL is copied to clipboard (e.g., `ipfs://QmXxxx...` or gateway URL)

#### Scenario: Share confirmation appears
- **WHEN** user clicks "Share" on a private analysis
- **THEN** a confirmation dialog explains the analysis will be public and requests approval
