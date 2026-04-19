# ADR 001: Parts List and Parts Sub Models

**Date:** 2024-06-09  
**Status:** Accepted

## Decision
Implement PartsList and PartsSub models in `src/ith_webapp/models/parts_list.py` to support the Bill of Materials (BOM) and parent-child line items as required by F-026.

## Context
The system requires a Bill of Materials (BOM) feature, mapping to Access Parts List Assembly forms and reports. This necessitates a PartsList model (for the main BOM) and a PartsSub model (for subcomponents/line items).

## Alternatives Considered
- **Single Table Model:** Rejected due to lack of flexibility for parent-child relationships.
- **No ORM Models:** Rejected; ORM models are standard for maintainability and integration.

## Implementation Details
- Created `PartsList` and `PartsSub` SQLAlchemy models in `src/ith_webapp/models/parts_list.py`.
- Each model includes basic fields as per initial requirements.
- Tests added in `tests/unit/test_parts_list_model.py`.

## Validation
- Unit tests confirm model instantiation and field presence.
- All tests pass after implementation.

## Consequences
- Enables future expansion for BOM logic and relationships.
- Aligns with project ORM and testing standards.

## References
- F-026 in prd.json
- `src/ith_webapp/models/parts_list.py`
- `tests/unit/test_parts_list_model.py`
