## Why

Analyzed tracks are currently stored only locally on each user's machine. By publishing analysis metadata to IPFS, musicians can build a shared, decentralized library of improvisation guides. This creates a community resource where users discover analyses, learn from each other's insights, and contribute back.

## What Changes

- Publish analysis metadata (key, chords, patterns, tips) to IPFS with content hash
- Create a local index mapping track (artist, title) to IPFS content hash
- Add share/publish button on track detail page
- Add discovery/search interface to find shared analyses from other users
- Store public/private flag per analysis (default: public)
- Allow users to pin/download analyses from IPFS and import them locally

## Capabilities

### New Capabilities
- `ipfs-publish-analysis`: Publish analysis data to IPFS and get a persistent content hash
- `ipfs-discovery`: Search and discover published analyses from the IPFS network
- `ipfs-import-analysis`: Download and import shared analyses from IPFS into local database
- `analysis-sharing-control`: Toggle public/private status per analysis
- `analysis-metadata-indexing`: Create searchable metadata (artist, title, key, tempo) for discovery

### Modified Capabilities
- `track-detail-view`: Add share/publish button and public status indicator to track detail page
- `track-management`: Support importing/syncing analyses from IPFS alongside local uploads

## Impact

- **Frontend**: Add share button, discovery search interface, import UI in track detail and index pages
- **Backend**: Integrate IPFS client (go-ipfs or js-ipfs), create publishing/fetching functions in new `ipfs.py` module
- **Database**: Track IPFS content hash, publication timestamp, public/private flag per analysis
- **Dependencies**: IPFS client library (ipfshttpclient for Python), metadata indexing (optional: simple SQLite full-text search)
- **Network**: No new external APIs except IPFS daemon/gateway
- **User Experience**: Users can opt-in to share; discovery is read-only to avoid spam
