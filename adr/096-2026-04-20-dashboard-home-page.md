# ADR 096: Dashboard Home Page

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-096 dashboard landing page, summary visibility, recent activity, quick access navigation
- **Tags**: dashboard, navigation, landing-page, summary, audit-trail
- **Supersedes**: ADR 043

## Decision
Replace the root switchboard landing page with a dashboard home page that shows summary counts, recent activity, and quick-access links to common workflows.

## Context
The previous landing page was a pure navigation switchboard. That structure was useful for route discovery, but it did not surface operational status that users need on entry. The backlog now requires the home page to summarize open check-ins, pending quotes, ready-to-ship work, and open services while still preserving access to the major workflows.

## Alternatives Considered
### Keep the switchboard as the primary root page
- Rejected because it hides operational status behind a static menu.

### Redirect `/` to an existing workflow list
- Rejected because it would remove the application-level overview and recreate the Access-era navigation problem in a different form.

### Add a separate dashboard route and leave `/` unchanged
- Rejected because the primary entry point would remain the switchboard instead of the dashboard.

## Implementation Details
- Render `/` as `Dashboard - ITH` through the shared `base.html` layout.
- Calculate summary counts in the Flask app factory using the request-scoped SQLAlchemy session.
- Use these counts:
  - open check-ins: `CheckInSub` rows where `closed` is false
  - pending quotes: active `Service` rows with no `quoted_date` and no `completed_date`
  - ready to ship: `PackingList` row count
  - open services: active `Service` rows with no `completed_date`
- Show recent activity from `AuditTrail`, ordered newest-first.
- Keep quick links to common workflows such as Customer List, Open Repair List, Packing List Index, Ready to Ship, Field Services, Inventory Reorder Dashboard, and Audit Trail.

## Validation
- Added regression coverage for the dashboard landing page.
- Verified summary counts, recent activity, and quick-access links through unit tests.
- Ran the full pytest suite successfully.

## Consequences
### Positive
- Users see operational status immediately on entry.
- The root page remains a central navigation hub.
- Recent activity is visible without needing to open the audit trail report.

### Negative
- The root route now depends on several application models.
- Some dashboard counts are intentionally broad until dedicated workflow status fields exist.

### Neutral
- The previous switchboard structure is preserved as quick-access navigation rather than a full sectioned landing page.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metrics**: users can see summary counts and recent activity on the home page, and common workflows remain one click away.
- **Rollback strategy**: restore the switchboard sections if the dashboard becomes too dense or the count queries become too expensive.

## References
- `prd.json` F-096
- `src/ith_webapp/app.py`
- `src/ith_webapp/models/check_in.py`
- `src/ith_webapp/models/service.py`
- `src/ith_webapp/models/packing_list.py`
- `src/ith_webapp/models/audit_trail.py`
- `tests/unit/test_app.py`
