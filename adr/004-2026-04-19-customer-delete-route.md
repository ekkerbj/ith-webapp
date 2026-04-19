# ADR 004: Customer Delete Route Implementation

- **Date:** 2026-04-19
- **Status:** Accepted
- **Authors:** The AI
- **Drivers:** RESTful API consistency, test-driven development, maintainability
- **Tags:** customer, delete, REST, Flask, SQLAlchemy
- **Supersedes/Superseded By:** None

## Decision
Implement a POST /customers/<id>/delete route in the Flask app to support customer deletion, with redirect to the customer list and test coverage.

## Context
The project required a way to delete customers via the web interface, matching CRUD conventions. The test suite expected a /customers/<id>/delete POST endpoint that removes a customer and redirects to the list. No such route existed, causing test failures.

## Alternatives Considered
- **DELETE HTTP method:** Not chosen due to browser form limitations and test expectations for POST.
- **Soft delete:** Not required by current requirements; implemented as hard delete.
- **AJAX/JS delete:** Not required; server-side POST sufficient for now.

## Implementation Details
- Added @bp.route("/<int:customer_id>/delete", methods=["POST"]) to customers.py.
- Route loads customer, deletes if found, commits, and redirects.
- Returns 404 if customer not found.
- Test verifies redirect and removal from list.

## Validation
- All unit tests pass, including test_customer_delete_removes_customer.
- Manual test via browser confirmed correct redirect and deletion.

## Consequences
- Enables customer deletion via UI and API.
- Aligns with RESTful conventions and test expectations.
- No protection yet against deleting customers with dependent records (future work).

## Monitoring & Rollback
- Review on next feature/test addition.
- Rollback: Remove route and restore test if needed.

## References
- tests/unit/test_customer_views.py
- src/ith_webapp/views/customers.py
- prd.json
