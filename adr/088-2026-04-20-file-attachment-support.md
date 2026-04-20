# ADR 088: Part File Attachment Support

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-088 backlog item, Access item attachment/image parity, low-dependency storage, deterministic retrieval
- Tags: parts, attachments, files, storage

## Decision
Implement file attachment support on parts using the local filesystem as the default storage backend, with upload and download routes under the parts blueprint.

## Context
The backlog requires support for item images and documents, matching Access Item Attachment and Item Image reports. The application already has a parts entity and a stable Flask blueprint, so the smallest reliable approach is to store attachments on disk and expose them through part-specific routes. This avoids adding a new database table or external storage dependency for the initial implementation.

## Alternatives Considered
- **Firebase Cloud Storage**: rejected for this increment because it would require new external configuration and credentials before the core attachment flow is available.
- **Database blob storage**: rejected because it would bloat the database and complicate backup/restore for file payloads.
- **No attachment support**: rejected because it would leave the backlog item incomplete.

## Implementation Details
- Added part attachment upload and download routes in `src/ith_webapp/views/parts.py`.
- Files are stored under `PART_ATTACHMENT_STORAGE_ROOT` when configured, otherwise under `instance/part_attachments/<part_id>/`.
- Filenames are sanitized with `secure_filename` before persistence and retrieval.
- Part detail rendering now lists attachments and shows inline previews for image files.

## Validation
- Added a unit test covering upload, persistence, detail rendering, and download retrieval.
- Ran the full test suite successfully (`pytest -q`).

## Consequences
- Attachment support is available without extra services or schema changes.
- Files remain easy to inspect and back up on disk.
- The implementation is simple, but duplicate filenames for the same part will overwrite prior files.

## Monitoring & Rollback
- Review if attachment volume grows or shared storage becomes necessary.
- Success metric: uploaded files remain downloadable and visible from the part detail page.
- Rollback strategy: remove the routes and filesystem helper, then revert to the prior part detail view.

## References
- `prd.json` F-088
- `src/ith_webapp/views/parts.py`
- `tests/unit/test_parts_views.py`
- `adr/087-2026-04-20-customer-specific-report-variants.md`
