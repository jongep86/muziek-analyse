## MODIFIED Requirements

### Requirement: Track detail page layout
The system SHALL display track analysis details organized in sections on the track detail page.

**Updated behavior**: The page now includes an audio player widget as the first interactive section, followed by the existing analysis sections.

#### Scenario: Track detail page loads
- **WHEN** user navigates to a track detail page
- **THEN** the page displays (in order):
  1. Track metadata cards (concert key, Bb key, Eb key, tempo, duration)
  2. Instrument transposition dropdown
  3. Audio player widget with controls
  4. Timeline with chord blocks
  5. Sections and chords details
  6. Patterns and melody analysis

#### Scenario: Audio player is visible and functional
- **WHEN** the page loads and the audio file exists
- **THEN** the player is fully interactive with play/pause, seek, and volume controls

#### Scenario: Audio player is disabled for missing files
- **WHEN** the page loads and the audio file is missing or inaccessible
- **THEN** the player is shown in a disabled state with an informational message

### Requirement: Responsive player layout
The system SHALL display the audio player in a way that works on desktop and mobile devices.

#### Scenario: Desktop view
- **WHEN** page is viewed on a desktop (width > 768px)
- **THEN** the player card is displayed at full width with controls in a single row

#### Scenario: Mobile view
- **WHEN** page is viewed on a mobile device (width < 768px)
- **THEN** the player card is displayed at full width and player controls are appropriately sized for touch interaction
