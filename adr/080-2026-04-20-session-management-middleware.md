# ADR 080: Session Management Middleware

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: F-080, session lifecycle consistency, reduced view duplication, request-scoped cleanup
- **Tags**: flask, middleware, session, sqlalchemy, refactor

## Decision

Add shared request-session helpers and register Flask teardown middleware so view modules can obtain a request-scoped SQLAlchemy session from one place.

## Context

Many view modules repeated the same pattern: fetch `SESSION_FACTORY`, create a session, use `try/finally`, and close the session manually. That duplicated lifecycle code across CRUD handlers and made future routes more expensive to add correctly.

## Alternatives Considered

### Keep per-view session creation and closing

- **Rejected**: duplicates lifecycle code in every route module and invites inconsistent cleanup.

### Add a per-view decorator only

- **Rejected**: still requires every route function to be wrapped and keeps session handling spread across many modules.

### Use a centralized middleware/helper pair

- **Accepted**: keeps session creation and teardown in one place while allowing views to call a shared `get_session()` helper.

## Implementation Details

- Added `src/ith_webapp/views/session.py` with `get_session()` and `register_session_middleware(app)`.
- `get_session()` stores the request session on `flask.g` so repeated lookups within one request return the same object.
- `register_session_middleware(app)` registers a `teardown_request` hook that closes and removes the request session.
- `create_app()` now registers the middleware after configuring the session factory.
- Session-using view modules delegate `_get_session()` to the shared helper instead of creating sessions directly.

## Validation

- Added a regression test that exercises a request-scoped session, verifies repeated lookups share the same object, and confirms the session closes after the response.
- Ran the full pytest suite successfully.

## Consequences

### Positive

- Session lifecycle behavior is centralized and testable.
- New views can reuse the shared helper without repeating factory lookup code.
- Request teardown guarantees cleanup even if a route exits early.

### Negative

- The app factory now owns another cross-cutting concern.
- Some view modules still contain `session.close()` cleanup until they are fully simplified.

### Neutral

- The shared helper keeps the current SQLAlchemy session factory contract intact.

## Monitoring & Rollback

- **Review date**: 2026-05-04
- **Success metrics**: session-using routes keep passing, request sessions close after each request, and new route modules use the shared helper.
- **Rollback strategy**: remove the shared helper and teardown hook, then restore per-view session creation if the abstraction causes regressions.

## References

- `prd.json` F-080
- `src/ith_webapp/app.py`
- `src/ith_webapp/views/session.py`
- `tests/unit/test_session_management.py`
