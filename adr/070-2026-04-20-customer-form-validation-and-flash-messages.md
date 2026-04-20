# ADR 070: Customer Form Validation and Flash Messaging

**Date:** 2026-04-20  
**Status:** Accepted  
**Authors:** Copilot  
**Drivers:** F-070, user feedback, safer customer CRUD, consistent form handling

## Decision
Add server-side validation to customer create/edit flows and use flashed messages for success and error feedback. Invalid submissions stay on the form with inline field errors, while successful create/edit/delete actions flash a status message before redirecting.

## Context
Customer CRUD originally trusted request data directly, which allowed invalid integers or overlong values to raise exceptions during request handling. The backlog requires visible feedback for create/edit/delete flows, and the application already uses server-rendered templates that can render flashed messages without adding a client-side framework.

## Alternatives Considered
- **Rely on HTML-only validation:** Rejected because it does not protect server-side requests or provide consistent error handling.
- **Introduce a form library:** Rejected because the app only needs lightweight validation and already has a small, explicit request-to-model mapping.
- **Silently coerce bad values to null:** Rejected because it hides data entry mistakes and risks saving partial records.

## Implementation Details
- Added a customer form validation helper that checks required, integer, decimal, and length constraints before model construction.
- Preserved submitted values on validation failure so the form can be re-rendered with inline errors.
- Added flash messaging to customer create, edit, and delete handlers.
- Updated the shared base template to render flashed messages for all server-rendered pages.
- Kept the customer form template self-contained by displaying field-level errors next to the relevant inputs.

## Validation
- Added regression coverage for invalid customer submission, create success flash output, edit success flash output, and delete success flash output.
- Ran the customer view test suite successfully.
- Ran the full pytest suite successfully.

## Consequences
- Customer CRUD now fails fast on bad input and explains what needs correction.
- Flash messages provide consistent user feedback across redirect-based flows.
- The customer form template is larger, but the validation rules are explicit and close to the route handling code.

## Monitoring & Rollback
- **Review date:** 2026-05-04
- **Success metric:** customer CRUD requests no longer raise parse exceptions, and success/error feedback is visible after create/edit/delete actions.
- **Rollback strategy:** remove the validation helper, restore direct request parsing, and drop the shared flash rendering from `base.html`.

## References
- `prd.json` F-070
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/templates/customers/form.html`
- `src/ith_webapp/templates/base.html`
- `tests/unit/test_customer_views.py`
