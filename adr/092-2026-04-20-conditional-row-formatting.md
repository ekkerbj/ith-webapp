# ADR 092: Conditional Row Formatting

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Copilot
- **Drivers**: F-092, list readability, low-maintenance styling, pure CSS implementation
- **Tags**: css, tables, list-views, accessibility

## Decision
Apply shared CSS rules for table row striping and row highlighting across the server-rendered application. Use `tbody tr:nth-child(even)` for alternating rows and `tbody tr:hover, tbody tr:focus-within` for current-row emphasis.

## Context
The application already uses shared templates and a single stylesheet for table presentation. The Access backlog item behind F-092 called for conditional row formatting behavior that should not depend on JavaScript or per-view logic. A CSS-only approach keeps the implementation simple and consistent with the existing shared layout.

## Alternatives Considered
- **Add per-template row classes**: Rejected because it would duplicate logic across many list templates and require repeated view changes.
- **Use JavaScript to mark the active row**: Rejected because the behavior can be expressed with native CSS selectors and does not need client-side scripting.
- **Leave row formatting untouched**: Rejected because it leaves dense tables harder to scan and does not satisfy the backlog item.

## Implementation Details
- Added zebra striping and highlight rules to `src/ith_webapp/static/style.css`.
- Kept the change stylesheet-only so existing table-rendering templates did not need structural updates.
- Used `:focus-within` alongside `:hover` so keyboard navigation receives the same emphasis as mouse interaction.

## Validation
- Added a regression test that fetches `/static/style.css` and asserts the row-formatting selectors are present.
- Ran the full pytest suite successfully: 196 passed.

## Consequences
- List and table views are easier to scan without additional markup or scripting.
- The styling applies consistently wherever application tables are rendered.
- If future tables need different behavior, the selectors may need to be scoped more narrowly.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: list pages remain readable and row emphasis works for both pointer and keyboard navigation.
- **Rollback strategy**: remove the row-formatting selectors from `style.css` or scope them to a narrower table class if a page needs different treatment.

## References
- `prd.json` F-092
- `src/ith_webapp/static/style.css`
- `tests/unit/test_app.py`
