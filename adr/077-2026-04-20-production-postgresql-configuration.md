# ADR 077: Production PostgreSQL Configuration

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Production database connectivity, connection pooling, migration parity, Cloud Run compatibility
- **Tags**: architecture, database, postgresql, cloud-sql, alembic, deployment

## Decision

Use a PostgreSQL `DATABASE_URL` for production, enable SQLAlchemy pooling for PostgreSQL connections, and point Alembic migrations at the same production database URL.

## Context

The application currently defaults to SQLite for local development and tests. Production runs on Cloud Run and needs a PostgreSQL database that can be reached through Cloud SQL Auth Proxy or private IP using a standard SQLAlchemy PostgreSQL URL.

Production connections also need pooling and connection health checks so the app can reuse database connections efficiently under Cloud Run.

## Alternatives Considered

### Hardcode production database settings in code

- **Rejected**: couples deployment details to the application and blocks environment-based configuration.

### Keep Alembic on SQLite defaults

- **Rejected**: migrations would not target the production schema.

### Separate migration configuration from the app

- **Rejected**: duplicates database URL handling and increases drift risk.

## Implementation Details

- `src/ith_webapp/app.py` now reads `DATABASE_URL` from the environment when not testing.
- `src/ith_webapp/database.py` enables PostgreSQL pooling with `pool_pre_ping`, `pool_size`, and `max_overflow`.
- `migrations/env.py` now uses the same `DATABASE_URL` value for offline and online Alembic runs.
- Cloud SQL Auth Proxy and private IP are both supported by supplying a PostgreSQL URL that points at the reachable endpoint.

## Validation

- Added tests for PostgreSQL pooling configuration.
- Added tests for environment-driven database URL selection in the app factory.
- Full test suite passes after the change.

## Consequences

### Positive

- Production and migration code now target the same database URL.
- PostgreSQL connections are managed with pooling instead of one-off connections.
- Deployment can use Cloud SQL Auth Proxy or private IP without code changes.

### Negative

- Deployment now depends on a correctly supplied `DATABASE_URL`.
- Production migration execution must be run with the same environment configuration.

### Neutral

- SQLite remains the default for local development and tests unless overridden.

## Monitoring & Rollback

- **Review date**: After the first production PostgreSQL deployment
- **Success metrics**: app starts with PostgreSQL, migrations apply cleanly, connection reuse remains stable under load
- **Rollback strategy**: revert to the prior SQLite-only configuration and redeploy if production connectivity fails

## References

- `src/ith_webapp/app.py`
- `src/ith_webapp/database.py`
- `migrations/env.py`
- `alembic.ini`
- `Dockerfile`
- `cloudbuild.yaml`
