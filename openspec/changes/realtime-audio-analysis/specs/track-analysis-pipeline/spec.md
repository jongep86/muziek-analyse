## MODIFIED Requirements

### Requirement: Analyse audio tracks
The system SHALL extract musical features (key, BPM, chords, sections, melody) from audio files.

**Updated behavior**: Analysis now works on chunks during upload/import, producing preliminary results after 30-60 seconds and complete results when full audio is available.

#### Scenario: Fast pass produces initial results
- **WHEN** the first 30-60 seconds of audio are analysed
- **THEN** key, confidence, and BPM are detected and saved as "partial" results

#### Scenario: Full pass completes comprehensive analysis
- **WHEN** the complete audio file has been processed
- **THEN** chords, sections, melody, patterns, and other detailed features are available

#### Scenario: Results transition from partial to complete
- **WHEN** fast pass completes and full pass begins, then full pass completes
- **THEN** the database is updated with `_meta.status: 'complete'` and all analysis data replaces the preliminary data

#### Scenario: Cancellation preserves partial results
- **WHEN** analysis is cancelled after preliminary results but before completion
- **THEN** the database retains the partial results and marked as incomplete for user visibility

### Requirement: Support two-phase analysis
The analysis pipeline SHALL support both fast (preliminary) and full (comprehensive) analysis modes.

#### Scenario: Fast analysis extracts essential features
- **WHEN** fast pass mode is used on first 30-60s
- **THEN** key, BPM, and confidence are extracted efficiently (< 10 seconds)

#### Scenario: Full analysis is thorough
- **WHEN** full pass mode is used on complete audio
- **THEN** all features (key, BPM, chords, sections, melody, patterns, tips) are extracted accurately
