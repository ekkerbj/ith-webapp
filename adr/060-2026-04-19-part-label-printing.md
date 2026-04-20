# ADR 060: Part Label Printing

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Replace Access part label reports, keep label rendering deterministic, reuse the new barcode service, support multiple printable label formats
- **Tags**: architecture, labels, parts, barcode, html, printing
- **Supersedes**: None
- **Superseded By**: None

## Decision

The webapp will serve printable part labels from the parts blueprint at `/parts/<part_id>/labels`, rendering an HTML label sheet that embeds Code128 barcode SVG output and supports label format selection via a query parameter.

## Context

The Access application exposes many part label variants with different physical sizes. The webapp already stores the core part data needed for labels and now has SVG barcode generation available, so labels can be rendered directly in HTML without introducing a separate PDF pipeline.

## Alternatives Considered

### Generate PDF labels

- **Pros**: Directly matches a print-oriented output format.
- **Cons**: Adds more rendering code and a separate PDF layout surface for each label size.
- **Rejected**: HTML plus browser print styling is simpler and easier to extend for the initial migration.

### Store label templates in the database

- **Pros**: Could mirror the Access report catalog more closely.
- **Cons**: Extra schema and CRUD surface for a feature that is mostly static.
- **Rejected**: The current requirement is better served by code-driven templates.

### Rasterize barcode images

- **Pros**: Fits some legacy document workflows.
- **Cons**: More dependencies and less flexible embedding than SVG.
- **Rejected**: SVG remains the smallest deterministic output for labels.

## Implementation Details

- Add a `/parts/<part_id>/labels` route to `src/ith_webapp/views/parts.py`.
- Reuse `generate_code128_svg()` for the part number barcode.
- Render the label sheet with `render_template_string()` so the first version stays self-contained.
- Support the `format` query parameter with short, long, multi, kit, and custom variants.
- Include item code, description, and warehouse text in the rendered label.

## Validation

- Added a unit test that verifies the labels route returns HTML containing the part number, description, warehouse text, and an embedded SVG barcode.
- Verified the full test suite passes after implementation.

## Consequences

- **Positive**: Part labels are now printable without a separate document subsystem.
- **Positive**: The route reuses the existing parts model and barcode service.
- **Negative**: Browser print styling must carry the layout burden for now.
- **Neutral**: Future Access label variants can be mapped into the same route or split into dedicated templates later.

## Monitoring & Rollback

- **Review date**: When calibration and customer-specific label work is implemented.
- **Success metrics**: Part labels render correctly across the supported format variants and remain easy to print.
- **Rollback strategy**: Replace the HTML route with a dedicated PDF or template-backed label renderer if print fidelity requires it.

## References

- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/services/barcode_generation.py`
- `tests/unit/test_parts_views.py`
- `prd.json`
