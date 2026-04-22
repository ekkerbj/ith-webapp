# ADR 102: Local Import Database Startup Contract

## Metadata
- **Date**: 2026-04-22
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: local onboarding, imported Access dataset, browser demo stability, startup discoverability
- **Tags**: sqlite, local-dev, access, startup, documentation

## Decision
Use `sqlite:///ith_import.db` as the default local database for the imported Access dataset, and document that `./start.sh` is the supported local startup path for browsing the seeded data.

## Context
The repository ships an imported SQLite database populated from the legacy Access source. Developers and browser sessions need a predictable way to launch the app against that seeded data. The plain Flask startup command can still be used for empty-database development, but the import-backed database is the preferred local browsing path.

## Alternatives Considered

### Keep the app factory default at `ith.db`
- **Rejected**: too easy to start the app against an empty database and mistake that for missing data.

### Require an environment variable for every local run
- **Rejected**: adds friction to the common local browsing path.

### Bundle the imported data into the application package
- **Rejected**: makes data refreshes and source-of-truth separation harder.

## Implementation Details
- `create_app()` defaults to `sqlite:///ith_import.db` when `DATABASE_URL` is unset.
- `start.sh` launches Flask with the imported database and a development-friendly secret key.
- `README.md` and `LOCAL_SETUP.md` document the imported database as the normal local browsing path.
- Browser demo login uses a local fallback credential pair when Firebase is not configured.

## Validation
- Verified the `ith_import.db` file exists and contains the Access-imported tables.
- Confirmed the app boots against the imported database in local development.
- Full automated test suite passes.

## Consequences
- New developers can browse real data immediately with `./start.sh`.
- Empty SQLite startup remains available for isolated development and tests.
- The app now has an explicit local demo login path when Firebase is absent.

## Monitoring & Rollback
- **Review date**: after the next data-refresh cycle
- **Success metric**: local browser sessions reach seeded data without manual database configuration
- **Rollback strategy**: revert the default database and startup contract if the imported file ceases to be the normal local data source

## References
- `start.sh`
- `README.md`
- `LOCAL_SETUP.md`
- `src/ith_webapp/app.py`
- `ith_import.db`
