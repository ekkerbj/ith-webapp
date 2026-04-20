# ADR 064: Demo Contracts Reuse Rental Storage

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-064 demo contract backlog item, existing rental schema, minimize schema duplication
- Tags: demo-contract, rental, PDF, Flask, CRUD, reuse
- Supersedes: None
- Superseded By: None

## Decision
Implement demo contract behavior as a rental alias: reuse `Rental` and `RentalStatus` for storage, expose `/demo-contracts` CRUD views, and add a `/reports/demo-contract/<id>` PDF route.

## Context
F-064 requires a demo/loaner contract form and PDF report for customer equipment loans. The repository already has a working rental model, lookup table, CRUD views, and data relationships that match the same business shape, so a duplicate schema would add maintenance cost without new behavior.

## Alternatives Considered
- Add new `DemoContract` and `DemoContractStatus` tables: rejected because it duplicates the existing rental lifecycle and requires new migration and model plumbing.
- Map demo contracts onto a generic document table: rejected because it weakens type safety and obscures the existing equipment-loan structure.
- Reuse rental storage with demo-contract routes: accepted because it preserves behavior, keeps the schema stable, and matches the feature’s domain closely enough.

## Implementation Details
- Added `src/ith_webapp/views/demo_contracts.py` with list, detail, create, edit, and delete routes.
- Added a PDF builder and `/reports/demo-contract/<id>` route in `src/ith_webapp/reports.py`.
- Registered the blueprint in `src/ith_webapp/app.py` and exposed it on the switchboard.
- Kept the `Rental` table and `RentalStatus` lookup table as the source of truth.

## Validation
- `pytest -q tests/unit/test_demo_contracts.py` passes.
- `pytest -q tests` passes.
- The new tests cover list/detail rendering, create/edit/delete redirects, and PDF output.

## Consequences
- No new database tables or migrations are required.
- Demo contracts share rental data, so changes to rental semantics affect both surfaces.
- The codebase gains a second customer-facing route set over the same storage, which is simple but intentionally duplicated at the presentation layer.

## Monitoring & Rollback
- Review after the next loaner-equipment feature lands.
- Rollback by removing the demo-contract blueprint, report route, switchboard link, and tests if a separate schema becomes necessary later.

## References
- `prd.json` F-064
- `src/ith_webapp/views/demo_contracts.py`
- `src/ith_webapp/reports.py`
- `tests/unit/test_demo_contracts.py`
