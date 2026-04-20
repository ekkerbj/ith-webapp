# ADR 041: Firebase Authentication and Session Gating

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-041 login requirement, removal of local AD auth, Flask session management, protected routes
- **Tags**: authentication, Firebase, Flask, sessions

## Decision
Use Firebase Authentication email/password sign-in for the webapp, store the authenticated Firebase identity in the Flask session, and gate protected routes with a request hook that redirects anonymous users to `/login`.

## Context
The backlog requires replacing the legacy LocalUser/AD-based login flow with Firebase Auth. The application is server-rendered Flask, so the simplest reliable integration is a form-based login that exchanges email and password against Firebase and then persists the signed-in identity in the Flask session.

The existing test suite builds many `create_app(testing=True)` instances directly, so test runs need an auth-bypass switch to preserve current request tests while still enforcing auth in production and auth-specific tests.

## Alternatives Considered

### Firebase ID token verification on every request
- **Rejected**: adds per-request verification complexity and requires client-side token acquisition flow not present in the current server-rendered app.

### Server-side username/password storage
- **Rejected**: duplicates authentication concerns already provided by Firebase and reintroduces local credential management.

### Leave routes public and rely only on login page presence
- **Rejected**: does not satisfy the requirement that protected routes require authentication.

## Implementation Details
- Add `/login` GET and POST handlers.
- POST `/login` calls a Firebase auth client, defaulting to the Identity Toolkit REST API when no test double is configured.
- Store the authenticated user payload in `session["firebase_user"]`.
- Add `/logout` to clear the Flask session.
- Add a `before_request` guard that redirects anonymous requests to `/login?next=...`.
- Add `AUTH_REQUIRED` as an app config switch so tests can opt into or out of route protection explicitly.

## Validation
- Added unit tests for anonymous redirect and successful login session persistence.
- Ran the full pytest suite: 99 passed.

## Consequences
- Production routes are protected without adding a separate auth subsystem.
- Login state is centralized in the Flask session.
- Tests can remain fast and deterministic by injecting a fake Firebase auth client.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: authenticated users can reach protected views; anonymous users are redirected to login.
- **Rollback strategy**: disable `AUTH_REQUIRED` or remove the request hook and login routes if the auth flow must be replaced.

## References
- `prd.json` F-041
- `src/ith_webapp/app.py`
- `tests/unit/test_auth.py`
