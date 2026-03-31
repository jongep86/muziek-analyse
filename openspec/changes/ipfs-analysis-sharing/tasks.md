## 1. IPFS Setup & Integration

- [ ] 1.1 Add IPFS client library to requirements.txt
  - Add `ipfshttpclient` (Python IPFS HTTP client)
  - Alternative: use public gateway without local node setup
- [ ] 1.2 Create `ipfs.py` module with core functions
  - `publish_analysis(analysis_dict, metadata)` → returns content hash
  - `fetch_analysis(content_hash)` → retrieves analysis from IPFS
  - `configure_ipfs_endpoint()` → setup local node or gateway URL
- [ ] 1.3 Update `config.py`
  - Add `IPFS_ENDPOINT` (default to public gateway)
  - Add `IPFS_TIMEOUT` (30s default)
  - Add `SHARE_UPLOAD_USERNAME` (optional, for attribution)

## 2. Database Schema Updates

- [ ] 2.1 Add sharing columns to tracks table
  - `ipfs_hash` (VARCHAR) — content hash if shared, NULL if private
  - `is_shared` (BOOLEAN) — true if publicly shared
  - `shared_at` (TIMESTAMP) — when analysis was published
  - `original_uploader` (VARCHAR) — optional, for imported analyses
- [ ] 2.2 Create `ipfs_index` table for discovery search
  - Columns: id, artist, title, key, bpm, ipfs_hash, shared_at, uploader
  - Add full-text search index on (artist, title)
- [ ] 2.3 Migrate existing data
  - Set `is_shared = FALSE`, `ipfs_hash = NULL` for all existing tracks
  - Create migration script if using Alembic or similar

## 3. Analysis Publishing UI & Logic

- [ ] 3.1 Add "Share" button to track_detail.html
  - Button is hidden if already shared (show "Unshare" instead)
  - Button is disabled if analysis is not complete (partial results)
- [ ] 3.2 Implement share endpoint in app.py
  - POST `/tracks/<id>/share` endpoint
  - Validates track exists and is complete
  - Calls `ipfs_publish()` to upload to IPFS
  - Stores content hash and updates database
  - Returns success message with shareable link
- [ ] 3.3 Add confirmation dialog before first share
  - Explain that analysis becomes public
  - Show shareable link preview
  - Require explicit confirmation
- [ ] 3.4 Add "Unshare" button logic
  - POST `/tracks/<id>/unshare` endpoint
  - Sets `is_shared = FALSE` but keeps ipfs_hash (immutable content remains)
  - Updates UI to show "Private" badge

## 4. Discovery Interface

- [ ] 4.1 Create `/discover` route in app.py
  - GET endpoint that serves discovery page
  - Passes local index data to template
- [ ] 4.2 Build discovery.html template
  - Search bar (artist, title, key, tempo)
  - Results list showing shared analyses
  - Pagination (show 20 per page)
  - Sort by: recently shared, most popular (future), key, tempo
- [ ] 4.3 Implement search JavaScript
  - Full-text search against local SQLite index
  - Filter by key and tempo range
  - Highlight match terms in results
- [ ] 4.4 Add analysis preview modal
  - Click result to show read-only analysis detail
  - Display uploader and timestamp
  - Show "Import" button

## 5. Import & Integration

- [ ] 5.1 Implement import endpoint in app.py
  - POST `/tracks/import-ipfs` endpoint
  - Accepts content_hash in request
  - Fetches from IPFS via `ipfs_fetch()`
  - Creates new track with imported analysis
  - Stores original ipfs_hash and uploader metadata
- [ ] 5.2 Handle import conflicts
  - Detect if track already exists (by artist + title)
  - Show dialog with options: create version, overwrite, skip
  - Store multiple versions if user chooses
- [ ] 5.3 Add import button to discovery preview
  - Click "Import" fetches and imports that analysis
  - Show success/error toast notification
  - Redirect to new track detail after import

## 6. Metadata Indexing

- [ ] 6.1 Create indexing functions in models.py
  - `add_to_index(track)` — adds analysis to ipfs_index table
  - `remove_from_index(track)` — removes from search index
  - `search_index(query, filters)` — full-text search
- [ ] 6.2 Update share/unshare logic to update index
  - When sharing: call `add_to_index()`
  - When unsharing: call `remove_from_index()`
- [ ] 6.3 Build local SQLite full-text search
  - Use SQLite FTS5 (available in Python 3.8+)
  - Index artist, title, key fields
  - Support phrase search and filters

## 7. Track Detail Page Updates

- [ ] 7.1 Add share status display to track_detail.html
  - Show "Shared" badge with content hash if shared
  - Show "Private" badge if not shared
  - Add copy-to-clipboard button for IPFS link
- [ ] 7.2 Add share/unshare button with confirmation
  - "Share to IPFS" button if private
  - "Unshare" button if public
  - Confirmation dialog on first share
  - Success notification when published
- [ ] 7.3 Show version info for imported analyses
  - If analysis is imported, show "Imported from: [hash]"
  - Show original uploader if available
  - Option to "View Original" (fetch fresh from IPFS)

## 8. Track List Updates

- [ ] 8.1 Add share status column to track list (index.html)
  - Show small badge (🌐 for shared, 🔒 for private) per track
  - Sort option: "Show only shared" / "Show all"
- [ ] 8.2 Add filter/search for shared vs private
  - Add toggle or dropdown to filter display

## 9. Error Handling & Edge Cases

- [ ] 9.1 Handle IPFS connectivity issues
  - Graceful fallback if IPFS node/gateway is offline
  - Show helpful error message (suggest using public gateway)
  - Disable share button if IPFS unavailable
- [ ] 9.2 Handle duplicate track imports
  - Dialog when importing track that already exists
  - Option to create version (track_v2) or overwrite
- [ ] 9.3 Handle corrupted or invalid content
  - Validate imported JSON is valid analysis format
  - Show error if content hash doesn't point to valid analysis
  - Fall back gracefully

## 10. Documentation & Deployment

- [ ] 10.1 Update README.md
  - Explain sharing/discovery feature
  - Document IPFS setup (local node vs public gateway)
  - Explain that shared content is public and immutable
- [ ] 10.2 Update CLAUDE.md
  - Add IPFS sharing to feature list
  - Document architecture decisions
- [ ] 10.3 Create IPFS_SETUP.md guide
  - Instructions for installing IPFS locally (optional)
  - Public gateway setup
  - Troubleshooting common issues
- [ ] 10.4 Add database migration
  - SQLAlchemy or native SQL migration script for new columns/table
  - Ensure backward compatibility with existing data
- [ ] 10.5 Test sharing workflow end-to-end
  - Analyze track → share → get hash → import from hash → verify data
  - Test with multiple file formats and sizes
  - Test discovery search with various queries
- [ ] 10.6 Deploy to staging
  - Test with real IPFS network
  - Verify performance (publish/fetch timing)
  - Check for any network/connectivity issues
- [ ] 10.7 Deploy to production
  - Monitor IPFS gateway performance
  - Track user sharing patterns
  - Gather feedback on discovery interface

## 11. Optional Enhancements (Later)

- [ ] 11.1 Community statistics dashboard
  - Show total shared analyses, popular keys/tempos, trending artists
- [ ] 11.2 Analysis comparison tool
  - Side-by-side view of multiple analyses for same track
  - Highlight differences in chord detection, key, etc.
- [ ] 11.3 Reputation/rating system
  - Allow users to rate shared analyses
  - Show most-rated analyses in discovery
- [ ] 11.4 Versioning & collaboration
  - Track history of analysis versions
  - Collaborative editing (merge multiple analyses)
- [ ] 11.5 External indexer service
  - Build a web service that crawls IPFS and indexes all shared analyses
  - Provide API for better search/discovery
