# ADR 022: Packing List Workflow Views and Routing

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-024 requirement for workflow queue views
- Tags: workflow, packing list, routing, stub

## Decision
Implement stub Flask routes and blueprint for Packing List Workflow: /packing-lists/ready-to-produce and /packing-lists/ready-to-ship, returning 501 Not Implemented. This enables TDD for workflow queue features and unblocks further development.

## Context
F-024 requires two workflow queue views for packing lists: Ready to Produce and Ready to Ship. No prior routes or views existed. Stubs are needed to enable incremental TDD and to clarify routing structure.

## Alternatives Considered
- Implement full workflow logic immediately: Rejected, as TDD requires incremental, test-first development.
- Omit stub routes: Rejected, as this blocks test-driven progress and clear API contract.

## Implementation Details
- New blueprint: src/ith_webapp/views/packing_list_workflow.py
- Two routes: /packing-lists/ready-to-produce and /packing-lists/ready-to-ship
- Both return 501 Not Implemented for now
- Registered in app factory
- Unit test verifies 501 response

## Validation
- All tests pass after stub implementation
- Test for workflow routes returns 501 as expected

## Consequences
+ Enables TDD for workflow queue features
+ Clarifies API contract for workflow views
+ Unblocks further development

## Monitoring & Rollback
- Review after first implementation of workflow logic
- Rollback: Remove blueprint/routes if workflow is abandoned

## References
- F-024 in prd.json
- tests/unit/test_packing_list_workflow.py
