# ADR 101: Access Import CLI and Empty-DB Policy

## Metadata
- **Date**: 2026-04-22
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: initial Access data load, repeatable re-imports, local SQLite onboarding, fail-fast safety
- **Tags**: access, import, cli, sqlite, migration, etl

## Decision
Add an in-repo Access import helper and CLI that reads `access/*.accdb`, loads data into a fresh SQLite database, and refuses to run if the target database already contains rows.

## Context
The legacy system stores operational data in Access `.accdb` files. The web app needs a local path to pull that data into SQLite for development and verification, and the same path should remain usable for later production re-imports. The initial load must not overwrite an existing database.

## Alternatives Considered

### Alembic data migration only
- **Rejected**: good for one-off deployment steps, but awkward for repeatable local re-imports and source-file iteration.

### Manual export/import only
- **Rejected**: fragile, hard to test, and too dependent on ad hoc operator steps.

### Truncate-and-reload mode
- **Rejected**: too risky for the first working import path; empty-db import is safer and easier to reason about.

## Implementation Details
- Added `src/ith_webapp/services/access_migration.py` helpers for:
  - table ordering from SQLAlchemy metadata
  - empty-database validation
  - Access table discovery via `mdb-tables`
  - row export via `mdb-export`
  - field normalization and type coercion
- Added `src/ith_webapp/commands/import_access.py` as a reusable CLI entrypoint.
- The importer creates tables first, then validates emptiness, then loads Access rows in dependency order.
- Source rows with missing required fields are skipped instead of aborting the entire import.

## Validation
- Added unit coverage for Access row normalization, special-case audit-trail mapping, lookup-table mapping, empty-db enforcement, and import execution against a temporary SQLite file.
- Verified a full import into `ith_import.db` from `access/ITH_Data_TEST.accdb`.
- Full test suite passes.

## Consequences
- Local onboarding can be done from the Access source without manual row editing.
- The same import path can be reused later for production re-imports if needed.
- Some malformed source rows are skipped rather than corrected automatically.

## Monitoring & Rollback
- **Review date**: after the first real production re-import
- **Success metric**: imported SQLite counts match the expected Access data set for key tables
- **Rollback strategy**: remove the import CLI and helper module if the ETL model changes

## References
- `src/ith_webapp/services/access_migration.py`
- `src/ith_webapp/commands/import_access.py`
- `tests/unit/test_access_migration.py`
- `adr/078-2026-04-20-data-migration-from-access-to-postgresql.md`
- `adr/002-2026-04-19-alembic-migration-setup.md`
