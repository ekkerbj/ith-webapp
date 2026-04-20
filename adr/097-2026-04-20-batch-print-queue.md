# ADR 097: Batch Print Queue

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-097, combined print output, queued documents from list views, mixed HTML/PDF document support
- **Tags**: printing, queue, reports, iframes, html, pdf

## Decision
Add a batch print queue route that accepts multiple internal document URLs and renders them on one printable page.

## Context
The backlog requires a way to queue labels, certificates, and packing lists for batch printing. The application already exposes many printable documents as separate HTML and PDF routes, but it does not have a shared queue surface that can display multiple selected documents together.

## Alternatives Considered
- **Server-side PDF merging**: Rejected because the app already serves both HTML and PDF documents, and merging heterogeneous document formats would require a PDF parser or a major report refactor.
- **Open each selected document in a separate tab/window**: Rejected because it does not produce a single print queue page and makes batch printing awkward.
- **Add only links to the selected documents**: Rejected because it would not present a combined print output.

## Implementation Details
- Added `/reports/batch-print-queue` to render a queue page from repeated `url` query parameters.
- Validated each queued URL to keep the feature constrained to internal relative document URLs.
- Rendered each queued document in its own iframe so HTML labels and PDF reports can coexist on the same page.
- Kept the implementation self-contained in `src/ith_webapp/reports.py` so the queue reuses existing report and label routes without duplicating document-building logic.

## Validation
- Added regression coverage for the queue route rendering multiple selected documents.
- Ran the full pytest suite successfully: 203 passed.

## Consequences
### Positive
- Users can batch selected documents on a single page for printing.
- Existing report and label routes remain unchanged.
- Mixed HTML and PDF documents can be queued together.

### Negative
- The queue depends on browser iframe print behavior.
- The page is a print wrapper rather than a true server-side merged document.

### Neutral
- The route is generic and can support future document types without changing the queue page structure.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metrics**: queued documents load together, and the page prints correctly in supported browsers.
- **Rollback strategy**: remove the queue route and return to direct document links if iframe-based printing proves unreliable.

## References
- `prd.json` F-097
- `src/ith_webapp/reports.py`
- `tests/unit/test_batch_print_queue_report.py`
- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/views/ith_test_gauges.py`
- `src/ith_webapp/views/packing_list_workflow.py`
