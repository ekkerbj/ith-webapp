# ADR 089: Part Label Printing and Check-In Integration

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-089 backlog item, Access label parity, deterministic print data, check-in workflow integration
- Tags: parts, check-in, labels, reports, persistence
- Supersedes: None
- Superseded By: None

## Decision
Add a `part_label` table and `PartLabel` ORM model to store printable label snapshots created from check-in workflow data, and include those labels in the check-in PDF report.

## Context
The backlog requires a part label printing integration that originates from the check-in workflow. The application already has a stable check-in PDF report and an HTML part label renderer, so the smallest useful integration is to persist label snapshot data alongside check-ins and render it in the existing check-in document.

## Alternatives Considered
- **Generate labels only in-memory**: rejected because the label data would not be persisted for later printing or auditing.
- **Add a separate label blueprint first**: rejected because the backlog item is centered on check-in integration, not a standalone UI surface.
- **Attach labels to the part detail page only**: rejected because that would not capture the check-in-driven workflow described by the backlog.

## Implementation Details
- Introduce `PartLabel` in `src/ith_webapp/models/part_label.py`.
- Store `check_in_id`, optional `check_in_sub_id`, optional `part_id`, label text fields, quantity, and creation time.
- Add a `CheckIn.part_labels` relationship for cleanup and navigation.
- Extend `build_check_in_pdf()` so the check-in report renders a `Part Labels` section when label records exist.
- Add an Alembic migration for the new table.

## Validation
- Added a regression test that creates a `PartLabel` record and verifies the check-in PDF includes the label data.
- Ran the check-in report tests successfully after implementation.

## Consequences
- **Positive**: label print data is persisted and can be reproduced from a check-in record.
- **Positive**: the existing check-in report now reflects the label workflow without a separate subsystem.
- **Negative**: the new label table adds schema surface area and a migration.
- **Neutral**: future label templates can still be added without changing the storage contract.

## Monitoring & Rollback
- **Review date**: when a dedicated check-in UI is implemented.
- **Success metrics**: label data remains present in the check-in PDF and persists across database sessions.
- **Rollback strategy**: remove the report section, model, and migration if the workflow is replaced by a dedicated label queue.

## References
- `prd.json` F-089
- `src/ith_webapp/models/part_label.py`
- `src/ith_webapp/reports.py`
- `tests/unit/test_check_in_report.py`
- `migrations/versions/2026_04_20_03_add_part_label_table.py`
