# ADR 079: Error Handling and 404/500 Pages

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: F-079, user-facing error clarity, centralized exception handling, request-context logging
- **Tags**: flask, errors, logging, ux, observability

## Decision

Add custom 404 and 500 responses in the Flask application factory, and log unexpected exceptions with request metadata before returning the 500 page.

## Context

The application previously relied on Flask's default error pages. Those pages are functional but inconsistent with the rest of the server-rendered UI and do not provide project-specific navigation. The backlog also requires global exception handling and structured error logging so unexpected failures can be diagnosed with request path and method context.

## Alternatives Considered

### Keep Flask defaults

- **Rejected**: default pages are generic and do not match the rest of the application.

### Add per-blueprint error pages only

- **Rejected**: the error handling requirement is cross-cutting and should not be duplicated across every module.

### Raise uncaught exceptions to the WSGI server

- **Rejected**: loses user-friendly feedback and pushes all diagnostics into server logs without a consistent application-level response.

## Implementation Details

- Registered `404` and `Exception` handlers in `src/ith_webapp/app.py`.
- Rendered both error pages through the shared `base.html` layout so navigation and styling stay consistent.
- Returned a 404 page for missing routes and a 500 page for unhandled exceptions.
- Logged unexpected exceptions with `request.method`, `request.path`, and exception type using `app.logger.exception(...)` and `extra` metadata.
- Preserved `HTTPException` instances so explicit 400/403-style responses still behave normally.

## Validation

- Added regression coverage for a missing route returning the custom 404 page.
- Added regression coverage for an unhandled exception returning the custom 500 page and emitting structured log context.
- Ran the full pytest suite successfully.

## Consequences

### Positive

- Users get application-branded error pages instead of default framework responses.
- Operators get request-scoped context for unexpected failures.
- Error handling lives in one place instead of being scattered across view modules.

### Negative

- The app factory now owns another cross-cutting concern.
- The 500 page is intentionally generic, so debugging still depends on logs.

### Neutral

- The current implementation does not add custom 403 or 400 pages.

## Monitoring & Rollback

- **Review date**: 2026-05-04
- **Success metrics**: missing routes return the custom 404 page, unexpected exceptions return the custom 500 page, and logs include request context.
- **Rollback strategy**: remove the error handlers and restore Flask's default responses if the custom handling causes regressions.

## References

- `prd.json` F-079
- `src/ith_webapp/app.py`
- `src/ith_webapp/templates/base.html`
- `tests/unit/test_app.py`
