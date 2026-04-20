# ADR 067: Service Extended Fields

**Date:** 2026-04-20  
**Status:** Accepted  
**Authors:** Copilot  
**Drivers:** F-067, Access parity, service workflow completeness

## Decision
Extend the existing `Service` model with nullable columns for the common Access-style dates, assignment, status, tracking, and note fields needed by the service workflow.

## Context
The base service table only covered the minimum header fields. F-067 requires the service record to carry the broader workflow metadata used by quoting, follow-up, invoicing, and dispatch, and that data needs to stay queryable alongside the existing service header fields.

## Alternatives Considered
- **Separate detail table:** Rejected because these fields belong to the same service aggregate and are read together.
- **JSON blob for extras:** Rejected because it would make reporting, filtering, and validation harder.
- **Leave the table narrow:** Rejected because it blocks Access parity and future service work.

## Implementation Details
- Added nullable columns for received, quoted, and completed dates plus assignment and tracking metadata.
- Added customer/internal note fields as text columns to preserve longer workflow comments.
- Kept the existing service header fields intact so downstream reports continue to work without reshaping queries.
- Added a persistence test that exercises the extended constructor fields.

## Validation
- The service model test suite now covers extended field persistence.
- The full project test suite remains green after the model update.

## Consequences
- Service records can now store more workflow context without another join.
- The model is wider, but the extra columns keep the aggregate simple to use.
- Future service views and reports can consume the fields directly.

## Monitoring & Rollback
Review after the next service workflow task. Roll back by removing the added columns and the extended-field test if the shape proves too broad.

## References
- `src/ith_webapp/models/service.py`
- `tests/unit/test_service_model.py`
- `prd.json` F-067
