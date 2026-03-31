## Context

Musicians analyze tracks individually and store results locally. No mechanism exists to share these analyses or discover what others have analyzed. IPFS provides a decentralized, content-addressed way to publish and access this data without a central server.

The app already has analysis data (key, chords, patterns, tips) in JSON format, making it easy to publish to IPFS. Users have local analyses they may want to share.

## Goals / Non-Goals

**Goals:**
- Publish analysis metadata to IPFS with a persistent, shareable content hash
- Allow users to search/discover shared analyses (by track name, key, tempo)
- Import analyses from IPFS and integrate them into local database
- Users can toggle public/private on their own analyses
- Build a decentralized library of improvisation guides

**Non-Goals:**
- Share audio files (only analysis metadata)
- User authentication or reputation system
- Real-time collaboration or version control
- Monetization or payment channels
- Mobile-first discovery (web-only for now)

## Decisions

### 1. IPFS Publishing Architecture
**Decision:** Use a local IPFS node (or public gateway) to publish analysis JSON; store content hash in local database.

**Rationale:** Simple, no central server dependency, content-addressed (immutable by hash). Each analysis gets a deterministic hash that can be shared via link.

**Alternatives:**
- Publish to Ethereum (more decentralized but higher cost/complexity) — overkill for metadata
- Custom P2P network (more work, less battle-tested than IPFS)

### 2. Metadata Structure for Discovery
**Decision:** Wrap analysis JSON with metadata header (artist, title, key, BPM, uploader, timestamp).

**Rationale:** Enables searching without needing a central index. Metadata stays immutable with analysis.

**JSON structure:**
```json
{
  "_shared": {
    "artist": "Green Day",
    "title": "Boulevard of Broken Dreams",
    "shared_by": "musician_id or anon",
    "shared_at": "2026-03-31T12:00:00Z",
    "original_key": "Em",
    "original_bpm": 92
  },
  "analysis": { /* existing analysis data */ }
}
```

### 3. Local Index for Discovery
**Decision:** Maintain a local SQLite table of published analyses with full-text search on (artist, title, key).

**Rationale:** Enables fast local search without querying IPFS repeatedly. Users can build their own index by "pinning" shared analyses.

**Alternative:** Query IPFS DHT (decentralized hash table) — slower, requires IPFS node always running.

### 4. Public/Private Toggle
**Decision:** Per-analysis flag in database; unpublished analyses never go to IPFS.

**Rationale:** Users retain control. Only opt-in to sharing.

**Flow:**
- Analyze → stored locally with `is_shared: false`
- User clicks "Share" → publishes to IPFS, updates `is_shared: true` + stores content hash
- User clicks "Unshare" → sets `is_shared: false` but IPFS content remains (can't delete immutable content)

### 5. IPFS Access Method
**Decision:** Support both local IPFS node (for power users) and public gateway (for casual users).

**Rationale:** Flexibility. Local node = full decentralization; gateway = simpler setup.

**Config in `config.py`:**
```python
IPFS_API = "http://localhost:5001"  # local node or
IPFS_API = "https://gateway.ipfs.io"  # public gateway
```

## Risks / Trade-offs

**[IPFS node setup complexity]** → Users may not have IPFS running locally. *Mitigation:* Use public gateway by default; document self-hosting option.

**[Content immutability]** → Once published, analysis can't be edited or deleted (IPFS is immutable). *Mitigation:* Publish v2 as new hash; document versioning in metadata.

**[Discovery scalability]** → Local SQLite index doesn't scale to thousands of analyses. *Mitigation:* Index only analyses user has pinned; advanced users can run their own indexing service.

**[Privacy if using public gateway]** → Sharing via public gateway reveals IP address. *Mitigation:* Use Tor or VPN if privacy desired; document this.

**[Garbage collection]** → IPFS stores content indefinitely unless explicitly removed. *Mitigation:* Users manage their own IPFS storage; clearing local node also stops serving published content.

## Migration Plan

1. **Phase 1 (Setup):** Add IPFS client dependency, create `ipfs.py` module, add database columns for sharing
2. **Phase 2 (Publish):** Add share button and publish functionality to track detail page
3. **Phase 3 (Discover):** Build discovery search interface and import flow
4. **Phase 4 (Index):** Add local full-text search on downloaded metadata

## Open Questions

1. Should shared analyses include uploader name/ID or be anonymous?
2. Should there be a community site/webapp that indexes all shared analyses (beyond local search)?
3. How to handle naming conflicts (multiple "Boulevard of Broken Dreams" by different artists)?
4. Should users be able to "fork" a shared analysis and publish their own version?
