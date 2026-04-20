# ADR 071: Current-Month Date Filtering

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Copilot
- **Drivers**: F-071, Access-style MonthCompare behavior, current-period browsing, shared date logic
- **Tags**: date-filtering, month-compare, lists, dashboard, utilities

## Decision
Add a shared MonthCompare-style helper that determines whether a date falls in the current month and year, and use it to limit time-based list views to the current period.

## Context
The backlog requires a direct port of the legacy MonthCompare behavior from `modMonthCompare.txt`. The application has several transaction-style list views that should stay focused on the current month instead of mixing current and historical records.

## Alternatives Considered
- **Duplicate month/year checks in each view**: Rejected because it repeats the same logic and makes future fixes harder.
- **Filter only in templates**: Rejected because pagination and row counts would remain incorrect.
- **Introduce a heavyweight reporting layer**: Rejected because the need is limited to a simple reusable date predicate.

## Implementation Details
- Added `ith_webapp.services.date_filtering.month_compare()` for pure Python month/year comparison.
- Added `ith_webapp.services.date_filtering.current_month_filter()` for SQLAlchemy queries.
- Applied the shared filter to the rental, demo contract, field service, and order confirmation list routes.
- Kept the logic centralized so future month-based list views can reuse the same helper instead of reimplementing date math.

## Validation
- Added regression coverage for the MonthCompare helper, rental list filtering, and field service list filtering.
- Verified demo contract and order confirmation tests still pass.
- Ran the full pytest suite successfully: 160 passed.

## Consequences
- Current-period list views now stay focused on active records.
- Historical records remain in the database but no longer appear in these list pages by default.
- Shared date logic is easier to reuse for future month-based filters.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: current-month list pages exclude prior-month records while remaining pagination-aware.
- **Rollback strategy**: remove the shared helper and revert the view-level filters if the current-period browsing model changes.

## References
- `prd.json` F-071
- `src/ith_webapp/services/date_filtering.py`
- `src/ith_webapp/views/rentals.py`
- `src/ith_webapp/views/demo_contracts.py`
- `src/ith_webapp/views/field_service.py`
- `src/ith_webapp/views/order_confirmations.py`
- `tests/unit/test_month_compare.py`
- `tests/unit/test_rental_tracking.py`
- `tests/unit/test_field_service_views.py`
