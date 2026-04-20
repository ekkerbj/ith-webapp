# ADR 063: Customer Mailing and Address Labels

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: PRD F-063, Access label migration, deterministic print output, support for single and multi-label layouts
- **Tags**: architecture, labels, customers, address, html, printing
- **Supersedes**: None
- **Superseded By**: None

## Decision

The webapp will serve customer mailing labels, address labels, and SAP address labels from the customers blueprint at `/customers/labels/<variant>`, rendering HTML label sheets with selectable single or multi-label layouts.

## Context

The PRD requires migration of the Access mailing and address label reports. Customer and customer address data already exist in SQLAlchemy models, so the feature can be rendered directly in HTML without adding a separate document pipeline.

## Alternatives Considered

### Generate PDF labels

- **Pros**: Produces a print-focused artifact.
- **Cons**: Adds another rendering stack and more layout code.
- **Rejected**: HTML printing is sufficient for the first migration.

### Store label templates in the database

- **Pros**: Mirrors a report catalog.
- **Cons**: Extra schema and CRUD overhead for mostly static layouts.
- **Rejected**: Code-driven templates are simpler and easier to maintain.

### Add one route per Access report

- **Pros**: Direct mapping to legacy report names.
- **Cons**: More route duplication for essentially the same output family.
- **Rejected**: A small variant-based route keeps the implementation compact.

## Implementation Details

- Add a `/customers/labels/<variant>` route in `src/ith_webapp/views/customers.py`.
- Support `mailing`, `address`, and `sap` variants.
- Accept a `format` query parameter with `single` and `multi` values.
- Render customer name, card code, and the primary customer address in a shared label sheet template.
- Use deterministic ordering by customer ID and address ID.

## Validation

- Added unit coverage for mailing, address, and SAP label routes.
- Verified the full test suite passes after implementation.

## Consequences

- **Positive**: Customer label reports are available without introducing a PDF subsystem.
- **Positive**: The routes stay deterministic and easy to extend.
- **Negative**: Print fidelity depends on browser styling for now.
- **Neutral**: Additional Access label variants can be added as new route variants or template refinements later.

## Monitoring & Rollback

- **Review date**: When the next label family is migrated.
- **Success metrics**: All three label variants render correctly and remain easy to print.
- **Rollback strategy**: Replace the HTML route with a dedicated document renderer if print fidelity requires it.

## References

- `src/ith_webapp/views/customers.py`
- `tests/unit/test_customer_labels.py`
- `src/ith_webapp/models/customer.py`
- `src/ith_webapp/models/customer_address.py`
- `prd.json`
