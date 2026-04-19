# ADR 023: Packing List Header Model and Migration

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-022 requirement for packing list header CRUD
- Tags: packing list, model, migration, CRUD

## Decision
Implement PackingList SQLAlchemy model and Alembic migration for packing_list table, with at least an id primary key. Add PackingList to model registry and create a minimal test. This enables TDD for packing list header CRUD and unblocks downstream features.

## Context
F-022 requires a Packing List header model and CRUD. No prior model or migration existed. A minimal model and migration are needed to enable incremental TDD and to clarify the data structure.

## Alternatives Considered
- Implement full CRUD and all fields immediately: Rejected, as TDD requires incremental, test-first development.
- Omit model/migration: Rejected, as this blocks test-driven progress and clear schema contract.

## Implementation Details
- New model: src/ith_webapp/models/packing_list.py
- Table: packing_list (id primary key, more fields to be added incrementally)
- Alembic migration for packing_list table
- Model registered in __init__.py
- Minimal test for id field in test_packing_list_model.py

## Validation
- All tests pass after model and migration
- Test for PackingList.id passes

## Consequences
+ Enables TDD for packing list header CRUD
+ Clarifies schema contract for packing list
+ Unblocks further development

## Monitoring & Rollback
- Review after first CRUD implementation
- Rollback: Remove model/migration if feature is abandoned

## References
- F-022 in prd.json
- tests/unit/test_packing_list_model.py
