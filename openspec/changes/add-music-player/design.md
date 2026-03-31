## Context

The track detail page currently displays analysis data (chords, sections, note maps, patterns) but no audio playback. Users must leave the interface to listen to the audio. The proposal adds an HTML5 audio player integrated with the timeline so users can listen while reading the improvisation guide.

The project already has:
- Track file paths for both uploaded and YouTube-sourced audio
- A timeline visualization with chord blocks and time markers
- Dark theme CSS and responsive layout

## Goals / Non-Goals

**Goals:**
- Provide play/pause, seek, and volume controls in the web interface
- Synchronize playback position with timeline highlighting (show which chord is playing)
- Support both uploaded MP3/WAV files and YouTube-downloaded audio
- Match existing dark theme and layout
- No page reload required during playback

**Non-Goals:**
- Waveform visualization (can be added later)
- Audio effects or EQ controls
- Playlist or multi-track playback
- Server-side streaming or buffering optimization
- Audio analysis visualization (spectrograms, etc.)

## Decisions

### 1. HTML5 Audio Element
**Decision:** Use native `<audio>` tag instead of third-party player library.

**Rationale:** No new dependencies, full browser compatibility, sufficient controls for basic playback. Custom UI can be added with CSS/JS if styling is needed later.

**Alternatives:**
- Audio.js library (adds ~30KB, more customization) — not needed for basic player
- Plyr (lightweight wrapper, ~20KB) — overkill for current scope

### 2. Player Placement
**Decision:** Place player above the chord timeline, in its own section card.

**Rationale:** Logically separates playback controls from analysis visualization. Users see playback progress first, then detailed analysis below.

**Layout:** Player card → Timeline → Sections → Patterns

### 3. Timeline Sync
**Decision:** On `timeupdate` event, find the active chord and highlight its timeline block.

**Rationale:** Low-cost (no server calls), immediate visual feedback, helps users locate themselves in the song.

**Implementation:**
- Read `currentTime` from audio element
- Match against chord timestamps: `chord.start <= currentTime < chord.end`
- Add CSS class `active` to matching chord block
- Scroll timeline into view if needed

### 4. Audio Source Handling
**Decision:** Use existing `track.file_path` for both uploaded and YouTube tracks.

**Rationale:** YouTube tracks are already downloaded to disk by the YouTube import feature. No new download logic needed.

**Fallback:** If file not found, disable player and show message.

## Risks / Trade-offs

**[Seeking large files]** → File must be fully or progressively downloaded by the browser. Large WAV files may have buffering delays. *Mitigation:* Document file size limits in README; consider lossy encoding (MP3) for large files.

**[Timeline sync lag]** → If `timeupdate` fires infrequently (some browsers update every 250ms), user might not see exact chord highlight. *Mitigation:* Acceptable for learning — precision is not critical.

**[Mobile responsiveness]** → Audio player may take significant vertical space on phones. *Mitigation:* Use collapsible player or side-by-side layout on desktop only.

**[Browser compatibility]** → Older browsers (IE11) may not support HTML5 audio. *Mitigation:* Graceful degradation — player simply doesn't appear; analysis still visible.

## Migration Plan

1. **Deploy:** Add player HTML/CSS/JS to `track_detail.html`
2. **Test:** Play uploaded and YouTube tracks, verify sync and controls work
3. **Rollback:** Remove player card section from template (no data changes)
4. **Monitoring:** Watch for console errors related to missing audio files

## Open Questions

1. Should player be visible on the standalone HTML export (`export.py`)? (Current approach: no, since exported files are static)
2. Should we add a "download audio" button alongside the player for users who want a local copy?
3. What should happen if the audio file is deleted from disk after analysis? (Show error or disable player)
