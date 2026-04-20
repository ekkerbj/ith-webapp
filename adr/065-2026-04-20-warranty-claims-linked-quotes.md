# ADR 065: Warranty Claims with Linked Quotes

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-065 backlog item, claim traceability, linked quote history, lightweight CRUD support
- **Tags**: warranty claims, service, quotes, Flask, SQLAlchemy

## Decision
Implement warranty claims as a dedicated `WarrantyClaim` table with a linked `WarrantyClaimQuote` association table to capture multiple service quote references per claim.

## Context
The backlog requires warranty claim tracking and reporting with linked multi-quote data. Warranty claims need their own lifecycle, but the important business relationship is the set of service quotes tied to each claim. A separate claim table keeps the workflow queryable while preserving quote history.

## Alternatives Considered

### Store claim data on `Service`
- **Pros**: fewer tables.
- **Cons**: cannot represent multiple claims or multiple linked quotes cleanly.
- **Rejected**: warranty claims are distinct records, not a service attribute.

### Use a single text field for quote IDs
- **Pros**: simplest schema.
- **Cons**: no referential integrity, hard to query, hard to validate.
- **Rejected**: multi-quote links need relational integrity.

## Implementation Details
- Added `src/ith_webapp/models/warranty_claim.py` with `WarrantyClaim` and `WarrantyClaimQuote`.
- Registered both models in `src/ith_webapp/models/__init__.py` so metadata creation includes the tables.
- Added `/warranty-claims` CRUD routes in `src/ith_webapp/views/warranty_claims.py`.
- Added the warranty claims link to the main switchboard in `src/ith_webapp/app.py`.
- Added an Alembic migration to create the claim and association tables.

## Validation
- Added unit tests for claim linking plus list/detail/create/edit/delete behavior.
- Ran the full pytest suite successfully.

## Consequences
- Warranty claims now have a durable schema with explicit quote references.
- The app gains another CRUD surface and another migration to maintain.
- Future report work can reuse the claim-to-quote linkage instead of reconstructing it from ad hoc data.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: claims continue to render with linked quote rows and round-trip through CRUD operations.
- **Rollback strategy**: remove the blueprint, migration, and model registration if a different warranty workflow is adopted later.

## References
- `prd.json` F-065
- `src/ith_webapp/models/warranty_claim.py`
- `src/ith_webapp/views/warranty_claims.py`
- `migrations/versions/2026_04_19_11_add_warranty_claim_tables.py`
- `tests/unit/test_warranty_claim_model.py`
- `tests/unit/test_warranty_claim_views.py`
