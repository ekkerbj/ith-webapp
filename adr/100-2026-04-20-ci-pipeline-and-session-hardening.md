# ADR 100: CI Pipeline and Session Hardening

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: secure-by-default auth handling, pre-merge validation, container build verification, reduced credential risk
- **Tags**: ci, github-actions, security, sessions, flask, deployment

## Decision
Add a single GitHub Actions CI workflow for automated test execution and container image creation, and harden Flask session/auth handling by minimizing session contents, requiring a real production secret key, and enforcing CSRF and secure cookie settings.

## Context
The application is moving toward production deployment through Cloud Run and Firebase Hosting. The codebase already uses Firebase Authentication for sign-in and Flask session state for request authorization. That makes session contents, cookie settings, and pre-merge validation part of the application's security boundary.

The team also wants a low-cost workflow that catches breakage before merge without introducing deployment automation yet.

## Alternatives Considered

### No CI pipeline
- **Rejected**: leaves test execution and image build verification manual, increasing the chance of broken or unreviewed changes reaching main.

### Add deploy automation immediately
- **Rejected**: deployment automation is useful, but the current need is to prove tests and build outputs first.

### Keep refresh tokens in the Flask session
- **Rejected**: increases the impact of cookie compromise and stores unnecessary auth material client-side.

### Use a client-side framework with token storage
- **Rejected**: would add complexity and expand the attack surface without a clear requirement.

## Implementation Details
- Add one GitHub Actions workflow with a `test` job on push and pull request events.
- Add a `build-image` job that depends on `test`, runs only on `main`, and publishes the image to GHCR.
- Require `SECRET_KEY` outside tests.
- Set `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE=Lax`, and secure-cookie behavior by default in production.
- Limit the session payload to `email`, `local_id`, and `role`.
- Add CSRF protection for mutating requests and embed a CSRF token in POST forms.

## Validation
- Added regression tests for secure cookie configuration, minimal session storage, and login form CSRF handling.
- Verified the new workflows are present in the repository.
- Full test suite passes: 214 passed.

## Consequences
### Positive
- Merge-time validation reduces the chance of regressions.
- Container builds are validated without needing to deploy.
- Session compromise has less value because refresh tokens are no longer stored in the browser session.
- CSRF protection is present for mutating requests.

### Negative
- Developers must provide `SECRET_KEY` in non-test runs.
- Login and other POST forms now require CSRF tokens.
- GHCR becomes part of the build pipeline.

### Neutral
- The image workflow is build-only for now and does not deploy.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metrics**: all PRs run tests, image builds succeed on `main`, and no production secret material is kept in browser sessions.
- **Rollback strategy**: remove the workflows, restore the prior session payload, and relax CSRF/cookie settings if they block required local or production flows.

## References
- `src/ith_webapp/app.py`
- `src/ith_webapp/templates/base.html`
- `src/ith_webapp/templates/crud/form.html`
- `src/ith_webapp/templates/crud/detail.html`
- `tests/unit/test_app.py`
- `tests/unit/test_auth.py`
- `.github/workflows/ci.yml`
- ADR 041: Firebase Authentication and Session Gating
- ADR 042: Role-Based Access Control
- ADR 002: Cloud Run and Firebase Hosting Deployment
