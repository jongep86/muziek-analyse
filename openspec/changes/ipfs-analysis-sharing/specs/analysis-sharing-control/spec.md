## ADDED Requirements

### Requirement: Toggle public/private status
The system SHALL allow users to control whether their analysis is publicly shared on IPFS.

#### Scenario: Analysis is private by default
- **WHEN** a new analysis is created
- **THEN** it defaults to private (not published) and not visible to other users

#### Scenario: User publishes analysis
- **WHEN** user clicks "Share" button on a private analysis
- **THEN** the analysis is published to IPFS and becomes publicly discoverable

#### Scenario: User unpublishes analysis
- **WHEN** user clicks "Unshare" on a public analysis
- **THEN** the analysis is marked as private; IPFS content remains but is no longer indexed for discovery

#### Scenario: Share status is shown
- **WHEN** viewing track detail
- **THEN** a badge or indicator shows whether the analysis is "Shared" or "Private"

### Requirement: Prevent accidental public sharing
The system SHALL confirm before publishing an analysis to IPFS.

#### Scenario: Confirmation dialog appears
- **WHEN** user clicks "Share" for the first time
- **THEN** a confirmation dialog explains that the analysis will be publicly accessible and asks for confirmation
