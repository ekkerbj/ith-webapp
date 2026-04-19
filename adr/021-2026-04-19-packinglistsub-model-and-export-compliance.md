# ADR 021: PackingListSub Model and Export Compliance Fields

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-023 requirement for export compliance on packing list sub-items
- Tags: model, migration, export compliance, packing list

## Decision
Implement a new `PackingListSub` SQLAlchemy model and corresponding `packing_list_sub` table to support line items on packing lists with export compliance fields: harm_number, EECN, DDTC, COO, in_bond_code.

## Context
Export compliance for shipped items requires tracking specific fields at the line-item level. The packing list sub-items must be modeled as a sub-resource of Packing List, with CRUD support and database migration.

## Alternatives Considered
- **Store fields on parent PackingList**: Rejected, as compliance data is per-item, not per-list.
- **Embed as JSON**: Rejected, as relational structure is required for queries and integrity.

## Implementation Details
- New model: `PackingListSub` in `src/ith_webapp/models/packing_list_sub.py`
- Migration: Alembic migration with correct revision lineage and merge
- Test: Unit test for model field assignment
- Model fields: id, packing_list_id (FK), harm_number, EECN, DDTC, COO, in_bond_code

## Validation
- Migration applies cleanly after merge
- Unit test passes for model instantiation and field assignment

## Consequences
- Enables per-item export compliance tracking
- Increases packing list model complexity
- Requires future CRUD and API support for sub-items

## Monitoring & Rollback
- Review: 2026-05-01
- Success: CRUD and reporting for export compliance fields
- Rollback: Drop table and remove model if not needed

## References
- F-023 in prd.json
- US export compliance documentation
