# ADR 019: Service Follow-Up Chain Workflow

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-019 requirement in prd.json
- Tags: workflow, service, follow-up, state-machine

## Decision
Implement a state-machine-like workflow for service follow-up using a list of defined stages (Follow Up, Follow UpA, ..., Follow Up5) and simple in-memory stage tracking on the Service model.

## Context
The Access database implements a follow-up chain as a series of queries (Follow Up, Follow UpA, etc.) to track service status. The new system must replicate this pipeline for tool service tracking and dashboarding.

## Alternatives Considered
- **Database-driven state**: Would require schema changes and migrations. Rejected for initial implementation due to complexity and lack of cross-request persistence requirement.
- **In-memory attribute**: Chosen for simplicity and testability. Sufficient for initial workflow logic and can be refactored to persistent storage if needed.

## Implementation Details
- Added `src/ith_webapp/services/service_follow_up_chain.py` with:
  - `SERVICE_FOLLOW_UP_STAGES` (ordered list of stages)
  - `get_service_stage(service)` and `advance_service_stage(service)`
- Stage is tracked via a private attribute on the Service instance for testability.
- Test in `tests/unit/test_service_follow_up_chain.py` verifies correct progression through all stages.

## Validation
- Unit test covers stage progression and initial state.
- All tests pass after implementation.

## Consequences
- **Positive**: Simple, testable, and easily extensible. No schema changes required.
- **Negative**: Not persistent across requests; will need refactor if persistence is required.
- **Neutral**: Follows TDD and Tidy First principles.

## Monitoring & Rollback
- Review after first integration with dashboard or multi-request workflow.
- Rollback: Remove or replace in-memory tracking with persistent field if needed.

## References
- prd.json F-019
- tests/unit/test_service_follow_up_chain.py
