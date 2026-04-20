# ADR 042: Role-Based Access Control

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-042 role enforcement, Firebase session identity, view/action authorization
- **Tags**: authentication, authorization, roles, Flask, Firebase

## Decision
Store a single application role in the Flask session after Firebase login and enforce access at request time. Treat `admin` as unrestricted, allow `sales` and `technician` to perform write actions only within their respective blueprint groups, allow `readonly` users to view read-only pages, and reserve audit trail access for `admin`.

## Context
The application already authenticates users through Firebase and stores the signed-in identity in the Flask session. The backlog now requires replacing legacy AD group checks with role-based access control so the app can distinguish between admin, sales, technician, and readonly users.

The codebase is server-rendered Flask, so the lowest-friction enforcement point is a `before_request` guard that can inspect the current endpoint, request method, and session role before any view logic runs.

## Alternatives Considered

### Per-view decorators on every route
- **Rejected**: precise, but it would require touching many blueprint modules and duplicate permission logic across the app.

### Database-backed role tables
- **Rejected**: adds schema and migration overhead without a current need for role administration UI.

### Client-side hiding only
- **Rejected**: does not enforce authorization and would leave protected actions callable directly.

## Implementation Details
- Store `firebase_user.role` in the session after login.
- Resolve the role from Firebase payload data when present, with `role` or `customClaims.role`.
- Add a request-time authorization check in `create_app()`.
- Permit read-only requests broadly, but block mutating views unless the role matches the owning domain.
- Reserve `/audit-trail/...` for `admin`.

## Validation
- Added a regression test for blocking readonly access to the customer create form.
- Ran the full pytest suite: 100 passed.

## Consequences
- Authorization is centralized and easy to extend.
- Existing tests and anonymous auth behavior remain stable.
- Future route additions must be categorized correctly or they will default to read access only.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: role-specific users can reach only the views and actions intended for them.
- **Rollback strategy**: remove the request guard and role resolution logic, or relax the role map if a route needs temporary broad access.

## References
- `prd.json` F-042
- `src/ith_webapp/app.py`
- `tests/unit/test_auth.py`
