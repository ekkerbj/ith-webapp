# ADR 083: Names and Credit Card Authorization Form PDF Reports

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: F-083 backlog item, Access report parity, printable contact list output, lightweight PDF reuse
- **Tags**: architecture, reporting, pdf, customer-contacts, forms
- **Supersedes**: None
- **Superseded By**: None

## Decision

Add PDF report endpoints in `src/ith_webapp/reports.py` for a customer contact names report and a credit card authorization form.

## Context

F-083 requires two legacy Access outputs: a names list and a credit card authorization form. The application already uses a small internal PDF builder for text-first reports, so these documents should follow the same pattern instead of introducing a new rendering dependency.

Customer contact data already exists in `CustomerContact`, while the authorization form is a printable document that does not require persistent data to render by default.

## Alternatives Considered

### Render both documents as HTML only

- **Rejected**: the backlog explicitly calls for PDF output.
- **Rejected**: HTML would not match the expected printable workflow.

### Build a new PDF template engine

- **Rejected**: unnecessary complexity for two text-heavy documents.
- **Rejected**: the existing PDF helper already supports the required output.

### Fold the names list into the customer detail report

- **Rejected**: the names list is a separate printable document with a different audience and export path.

## Implementation Details

- Added `build_names_pdf(session)` to query ordered `CustomerContact` rows joined to `Customer`.
- The names report emits customer, contact, email, phone, and position fields in a simple PDF layout.
- Added `build_credit_card_authorization_form_pdf()` for a reusable blank form with signature and date lines.
- Added PDF routes:
  - `/reports/names`
  - `/reports/credit-card-authorization-form`
  - `/reports/cc-form` as a short alias for the same form

## Validation

- Added unit coverage for both PDF routes and the contact data rendering.
- Full test suite passes after the change.

## Consequences

### Positive

- Customer contacts can now be exported as a printable PDF names list.
- The credit card authorization form is available as a consistent PDF download.
- The implementation stays aligned with the existing report module and PDF helper.

### Negative

- The blank authorization form is text-based and does not reproduce any richer Access layout details.

### Neutral

- The report module gains two small helpers and two route entries.

## Monitoring & Rollback

- **Review date**: After the next report backlog item lands
- **Success metrics**: both documents render as PDFs and remain compatible with the existing test suite
- **Rollback strategy**: remove the two builders, routes, related tests, and this ADR if the report surface changes

## References

- `prd.json` F-083
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/customer.py`
- `src/ith_webapp/models/customer_contact.py`
- `tests/unit/test_names_and_cc_form_report.py`
