# ADR 061: ITH Test Gauge Label Printing

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Replace Access gauge label reports, keep label output deterministic, reuse the barcode service, and support small printable calibration/certification labels
- **Tags**: architecture, labels, gauges, barcode, html, printing
- **Supersedes**: None
- **Superseded By**: None

## Decision

The webapp will serve printable ITH test gauge labels from the `ith_test_gauges` blueprint at `/ith-test-gauges/<id>/labels/calibration` and `/ith-test-gauges/<id>/labels/certification`, rendering HTML label sheets with embedded Code128 barcode SVG output.

## Context

The Access application exposes small gauge labels used for calibration and certification tracking. The webapp already stores the gauge name, serial number, type, and due dates needed for those labels, and it already has deterministic SVG barcode generation available for printable outputs.

## Alternatives Considered

### Generate PDF labels

- **Pros**: Directly matches a print-oriented output format.
- **Cons**: Adds another document rendering surface and more layout code.
- **Rejected**: HTML plus browser print styling is simpler for the first migration.

### Store labels in the database

- **Pros**: Could mirror the Access catalog more closely.
- **Cons**: Adds schema and CRUD overhead for mostly static templates.
- **Rejected**: Code-driven templates are sufficient for the current scope.

### Reuse the existing gauge certificate PDF

- **Pros**: Reuses the current gauge data path.
- **Cons**: The Access label reports are smaller and distinct from certificates.
- **Rejected**: Labels should be a separate printable surface.

## Implementation Details

- Add label routes to `src/ith_webapp/views/ith_test_gauges.py`.
- Render the labels with `render_template_string()` to keep the first implementation self-contained.
- Reuse `generate_code128_svg()` for the gauge serial number barcode.
- Include the gauge name, serial number, gauge type, and the relevant due date on each label.
- Provide separate calibration and certification label routes so the Access variants map cleanly.

## Validation

- Added unit tests that verify both label routes return HTML containing the label title, gauge data, and embedded SVG barcode output.
- Verified the full test suite passes after implementation.

## Consequences

- **Positive**: Gauge labels are printable without a separate report pipeline.
- **Positive**: The label output stays deterministic and reuses the shared barcode service.
- **Negative**: Browser print styling still carries the layout burden.
- **Neutral**: Future Access label variants can be added as additional routes or template variants.

## Monitoring & Rollback

- **Review date**: When customer-specific label work is implemented.
- **Success metrics**: Gauge labels render correctly, remain easy to print, and cover both calibration and certification flows.
- **Rollback strategy**: Replace the HTML routes with a dedicated PDF/template-backed renderer if print fidelity requires it.

## References

- `src/ith_webapp/views/ith_test_gauges.py`
- `src/ith_webapp/services/barcode_generation.py`
- `tests/unit/test_ith_test_gauge_views.py`
- `adr/060-2026-04-19-part-label-printing.md`
- `prd.json`
