## ADDED Requirements

### Requirement: Detect and refine chords in real-time
The system SHALL analyze audio chunks from the microphone and detect chords, continuously refining results as more audio arrives.

#### Scenario: Chord detection starts immediately
- **WHEN** audio streaming begins
- **THEN** the server receives the first chunk and runs chord detection
- **THEN** initial detected notes/chords are computed within 1 second of chunk arrival

#### Scenario: Results are refined with rolling window
- **WHEN** a new chunk arrives after the first
- **THEN** the server re-analyzes a rolling 30-second window of recent audio
- **THEN** chord detections are updated (may refine or change based on more context)
- **THEN** updated results are sent to the client showing refined chords

#### Scenario: Rolling refinement improves accuracy over time
- **WHEN** a user plays a single chord for 5+ seconds
- **THEN** chord detection confidence increases as more audio context arrives
- **THEN** the detected chord may narrow from "likely C" to "confident C major" to "C major 7th" as more notes are heard

#### Scenario: Detection includes note-by-note display
- **WHEN** chord detection runs
- **THEN** individual notes being played are detected (if monophonic or voiced distinctly)
- **THEN** detected notes are shown alongside chord analysis

#### Scenario: Partial or uncertain detections are labeled
- **WHEN** audio is insufficient to confidently identify a chord (e.g., first 2 seconds)
- **THEN** results are shown with "preliminary" or confidence label (e.g., "~70% confident: C major")
- **THEN** as more audio arrives, confidence increases
