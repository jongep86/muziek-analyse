## 1. Audio Player HTML & Styling

- [ ] 1.1 Add audio player HTML structure to `templates/track_detail.html` above the timeline
  - Include `<audio>` element with id `track-audio`
  - Add player controls container with play/pause button, volume slider, seek bar, time display
  - Wrap in a card/section matching existing style
- [ ] 1.2 Add CSS styles for the player in `templates/track_detail.html` or `static/style.css`
  - Style play/pause button, volume slider, seek bar for dark theme
  - Ensure responsive layout on mobile (touchable controls)
  - Style disabled state (opacity, cursor: not-allowed)
- [ ] 1.3 Set audio source based on track file path
  - In Jinja template, set `src` attribute of `<audio>` element to track file path
  - Handle missing files (show disabled state or hide player)

## 2. Player Controls JavaScript

- [ ] 2.1 Implement play/pause button logic in track_detail.html `<script>`
  - Toggle between play and pause states
  - Update button icon/text accordingly
  - Handle `play` and `pause` events from audio element
- [ ] 2.2 Implement seek functionality
  - Wire seek bar (input range) to audio `currentTime` property
  - Update seek bar position on `timeupdate` event
  - Allow user to click/drag seek bar to jump to new position
- [ ] 2.3 Implement volume control
  - Wire volume slider to audio `volume` property (0-1 range)
  - Display current volume percentage or level indicator
- [ ] 2.4 Implement time display
  - Show current time and total duration in MM:SS format
  - Update current time on `timeupdate` event
  - Display total duration on `loadedmetadata` event

## 3. Timeline Synchronization

- [ ] 3.1 Create function to find active chord based on playback time
  - Compare `audio.currentTime` with chord start/end times
  - Return active chord or null if between chords
- [ ] 3.2 Implement chord highlighting during playback
  - On `timeupdate` event, find active chord
  - Add CSS class (e.g., `active`) to the corresponding chord block in timeline
  - Remove class from previously active chord
- [ ] 3.3 Implement section highlighting during playback
  - Track active section alongside active chord
  - Add CSS class to section container when playback enters that section
  - Remove class when exiting section
- [ ] 3.4 Implement timeline auto-scroll
  - When active chord changes, use `scrollIntoView()` to bring it into viewport
  - Check if user is manually scrolling before auto-scrolling (optional: pause auto-scroll while user drags)

## 4. Audio File Handling

- [ ] 4.1 Add backend validation for file existence
  - Check if `track.file_path` exists before rendering page
  - Pass flag to template indicating whether audio is available
- [ ] 4.2 Handle both uploaded and YouTube tracks
  - Verify YouTube-downloaded files are in correct location
  - Use same player for both file types
- [ ] 4.3 Add error handling for missing/inaccessible files
  - Show disabled player with message "Audio file not found"
  - Gracefully degrade (don't crash page)

## 5. Testing & Polish

- [ ] 5.1 Test audio playback with uploaded MP3/WAV file
  - Play, pause, seek, volume controls work
  - Time display updates correctly
  - Duration displays correctly
- [ ] 5.2 Test audio playback with YouTube-sourced track
  - Downloaded audio plays correctly
  - Same controls and sync work as uploaded files
- [ ] 5.3 Test timeline synchronization
  - Chord highlighting follows playback position
  - Timeline auto-scrolls to show active chord
  - Section highlighting updates correctly
- [ ] 5.4 Test responsive design
  - Player controls are readable/touchable on mobile
  - Layout doesn't break on small screens
  - Seek bar and volume slider work on touch devices
- [ ] 5.5 Test missing file handling
  - Delete audio file and reload page
  - Player shows disabled state with clear message
  - Page doesn't error
- [ ] 5.6 Update README with player feature description
  - Mention audio playback capability
  - Note supported file formats
- [ ] 5.7 Commit and test on live server
  - Verify player works in production
  - Check for console errors or warnings

## 6. Optional Enhancements (Later)

- [ ] 6.1 Add waveform visualization (requires additional library)
- [ ] 6.2 Add keyboard shortcuts (spacebar for play/pause, arrow keys for seek)
- [ ] 6.3 Remember playback position per track in browser localStorage
- [ ] 6.4 Add playback speed control (0.5x, 1x, 1.5x, 2x)
