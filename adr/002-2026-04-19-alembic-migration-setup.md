# ADR 002: Alembic Migration Setup

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** Database versioning, dev/prod parity, maintainability  
**Tags:** database, migration, alembic, architecture

## Decision
Adopt Alembic for database schema versioning. Configure for both SQLite (dev/test) and PostgreSQL (production). Generate initial migration from SQLAlchemy models.

## Context
- Need for reliable, repeatable schema migrations across environments.
- Project uses SQLAlchemy ORM; models defined in Python.
- SQLite used for development/testing, PostgreSQL for production.

## Alternatives Considered
- Manual SQL scripts: error-prone, hard to maintain.
- Flask-Migrate: wrapper around Alembic, but direct Alembic use preferred for flexibility.
- Other migration tools (e.g., Django migrations): not compatible with SQLAlchemy.

## Implementation Details
- Ran `alembic init migrations` to scaffold migration environment.
- Configured `alembic.ini` for SQLite by default (`sqlalchemy.url = sqlite:///ith.db`).
- Updated `migrations/env.py` to use `Base.metadata` from project models.
- Generated initial migration with `alembic revision --autogenerate`.
- Applied migration with `alembic upgrade head`.
- All tests pass with Alembic-managed schema.

## Validation
- All automated tests pass after migration.
- Manual DB inspection confirms schema matches models.
- Migration applies cleanly to new SQLite DB.

## Consequences
**Positive:**
- Reliable, versioned schema changes.
- Easy onboarding for new developers.
- Consistent DB state across environments.

**Negative:**
- Slightly increased complexity in setup.
- Need to maintain migration scripts.

**Neutral:**
- Alembic is a standard tool for SQLAlchemy projects.

## Monitoring & Rollback
- Review migration scripts on each schema change.
- Rollback by reverting to previous migration revision if needed.

## References
- [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)