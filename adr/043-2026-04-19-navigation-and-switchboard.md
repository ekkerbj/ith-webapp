# ADR 043: Navigation and Switchboard

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-043 top-level navigation, Access switchboard replacement, route discoverability
- **Tags**: navigation, switchboard, Flask, UI

## Decision
Render the application root as a sectioned switchboard page instead of redirecting immediately to Customers. Organize the landing page around the backlog's top-level areas: Customers, Check In, Services, Packing Lists, Parts, Field Service, Reports, and Admin.

## Context
The legacy Access application used a switchboard form as the primary entry point for users. The Flask app already exposes several of the target workflows, but there was no dedicated landing page that grouped them into the same top-level structure. Redirecting `/` straight to Customers hid the broader application surface and made the navigation model inconsistent with the backlog.

## Alternatives Considered

### Keep `/` redirecting to Customers
- **Rejected**: preserves the existing behavior, but it does not provide a switchboard or top-level workflow grouping.

### Add a separate `/switchboard` route and keep `/` as-is
- **Rejected**: introduces a second landing page and leaves the primary entry point inconsistent with the Access-style navigation model.

### Client-side navigation only
- **Rejected**: would still require a landing page structure and would not improve server-rendered route discoverability.

## Implementation Details
- Change the root route to render a `Switchboard` page with `base.html`.
- Present each top-level area as a section with links to existing routes where available.
- Use placeholder text for areas that do not yet have dedicated routes.
- Reuse existing endpoints such as Customers, Projects, Order Confirmations, Consignment Lists, Packing List workflow views, Field Services, Wind Turbines, and the inventory reorder dashboard.

## Validation
- Added a regression test that asserts `/` returns the switchboard and includes all top-level section names.
- Ran the full pytest suite: 100 passed.

## Consequences
- Users now land on a navigation page that mirrors the legacy Access entry point.
- The app has a clearer top-level information architecture.
- Some sections remain placeholders until their dedicated workflows are implemented.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: users can reach the major application areas from the root landing page without needing a direct redirect.
- **Rollback strategy**: restore the redirect to Customers if the switchboard becomes confusing or the menu structure changes.

## References
- `prd.json` F-043
- `src/ith_webapp/app.py`
- `tests/unit/test_app.py`
