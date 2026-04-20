# ADR 066: Customer Extended Fields

**Date:** 2026-04-20  
**Status:** Accepted  
**Authors:** Copilot  
**Drivers:** F-066, SAP pricing compatibility, customer form completeness, Access parity

## Decision
Extend the existing `Customer` model with nullable columns for the commonly used account, contact, site, tax, shipping, and workflow fields, and surface them in grouped customer create/edit/detail views.

## Context
The current customer table only covered the base identity fields. The backlog requires a much broader Access-style customer record, and the application already reads customer pricing metadata such as `price_list_num`. Keeping the data on the same aggregate preserves the current query shape and avoids introducing a second customer profile table.

## Alternatives Considered
- **Separate profile tables:** Rejected because the customer screens and pricing code need direct access to the fields without join-heavy plumbing.
- **JSON blob for extra fields:** Rejected because it would weaken validation, queryability, and form rendering.
- **Leave the model narrow:** Rejected because it blocks the backlog item and leaves SAP/customer screens incomplete.

## Implementation Details
- Added nullable SQLAlchemy columns for price list, salesperson, territory, credit limit, tax, contact, site, shipping, and notes data.
- Added a `sales_rep` alias property for compatibility with common naming in forms and tests.
- Updated customer create/edit handling to map the new fields from request data.
- Reworked customer forms into fieldsets so the extended fields stay organized by category.

## Validation
- Added coverage for editing a customer with extended fields and confirming the rendered detail page shows the saved values.
- Confirmed the customer and SAP-focused test sets pass.
- Ran the full test suite successfully.

## Consequences
- Customer data is now broader and closer to the Access source shape.
- The form and detail views are larger, but the grouped layout keeps them readable.
- Future backlog items can reuse the same customer fields without additional schema work.

## Monitoring & Rollback
Review after the next customer-related backlog item. Roll back by removing the new columns, view bindings, and template sections if the shape proves too broad.

## References
- `src/ith_webapp/models/customer.py`
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/templates/customers/form.html`
- `src/ith_webapp/templates/customers/detail.html`
- `tests/unit/test_customer_views.py`
