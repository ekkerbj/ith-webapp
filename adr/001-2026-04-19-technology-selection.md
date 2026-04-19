# ADR 001: Technology Selection

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Minimal frontend JS, TDD discipline, relational data model compatibility, operational simplicity
- **Tags**: architecture, technology, python, flask, postgresql, firebase

## Decision

The ITH webapp will be built with:

- **Backend**: Python 3.12+ with Flask
- **Database**: PostgreSQL (Cloud SQL in production, SQLite for fast local tests)
- **ORM**: SQLAlchemy 2.x with Alembic for migrations
- **Frontend**: Server-rendered HTML (Jinja2 templates) + CSS + minimal vanilla JS
- **Authentication**: Firebase Authentication (Google Sign-In)
- **Hosting**: Firebase Hosting (static assets) + Cloud Run (Flask backend)
- **Reports/PDF**: WeasyPrint for server-side PDF generation
- **Barcodes**: python-barcode library
- **Testing**: pytest with pytest-cov
- **SAP integration**: Repository interface pattern; concrete implementation deferred

## Context

The system being replaced is a Microsoft Access split-database application with:

- 69 relational tables with 68 foreign key relationships
- 240 saved queries (mostly complex multi-table JOINs)
- 111 forms (80 with VBA code-behind)
- 206 reports
- 17 VBA modules with business logic
- ODBC-linked read access to ~30 SAP Business One tables

The data model is deeply relational. The application is form-driven CRUD with report generation. There is no requirement for real-time collaboration, complex client-side state, or SPA behavior.

The development team has a Java background but has chosen Python for this project. TDD (Red-Green-Refactor) is mandatory for all changes.

## Alternatives Considered

### Frontend framework (React/Vue/Angular)

- **Rejected**: The requirement is minimal JS. The Access app is server-driven (form submit, page reload). Server-rendered HTML with Jinja2 preserves this pattern with zero client-side build tooling.

### Firestore (document database)

- **Rejected**: The data model has 68 foreign key relationships and 240 queries with multi-table JOINs. Firestore would require extensive denormalization, losing the existing relational structure and making query translation impractical.

### Django instead of Flask

- **Considered**: Django provides more batteries (admin, ORM, auth). Rejected because: (a) SQLAlchemy provides a more explicit ORM that maps better to the existing Access schema; (b) Flask's simplicity suits a TDD-first approach where each component is added incrementally; (c) Django's admin panel is not needed — the app already has its own UI patterns.

### Java (Spring Boot)

- **Considered**: Familiar to the team. Rejected for this project because: (a) higher boilerplate for CRUD forms; (b) Jinja2 templates are simpler than Thymeleaf for server-rendered HTML; (c) Python's ecosystem for PDF generation and data manipulation is stronger for this use case.

### Cloud SQL vs. local PostgreSQL

- **Decision**: Use SQLite for unit/integration tests (fast, no setup), PostgreSQL for acceptance tests and production. SQLAlchemy abstracts the difference. Cloud SQL for PostgreSQL in production.

## Implementation Details

### Project structure

```
ith-webapp/
├── adr/                    # Architectural decision records
├── src/
│   └── ith_webapp/
│       ├── __init__.py
│       ├── app.py          # Flask application factory
│       ├── models/         # SQLAlchemy models
│       ├── repositories/   # Data access layer
│       ├── services/       # Business logic
│       ├── views/          # Flask route handlers
│       ├── templates/      # Jinja2 HTML templates
│       └── static/         # CSS, minimal JS
├── tests/
│   ├── unit/               # Fast, isolated, SQLite-backed
│   ├── integration/        # Database interaction tests
│   └── conftest.py         # Shared fixtures
├── migrations/             # Alembic migrations
├── pyproject.toml          # Project metadata and dependencies
└── .gitignore
```

### Layered architecture

1. **Models**: SQLAlchemy declarative models mapping 1:1 to Access/PostgreSQL tables
2. **Repositories**: Data access objects encapsulating queries; one per aggregate root
3. **Services**: Business logic (pricing waterfall, audit trail, etc.)
4. **Views**: Flask route handlers; thin — delegate to services
5. **Templates**: Jinja2 server-rendered HTML

### SAP abstraction

SAP data access is behind a repository interface. Initial implementation returns empty/stub data. Future options:

- Periodic ETL sync to local PostgreSQL tables
- SAP Business One Service Layer REST API
- Direct read replica access

The interface boundary ensures the webapp can be developed and tested without SAP connectivity.

### Testing strategy

- **Unit tests**: pytest + SQLite in-memory; test models, repositories, services in isolation
- **Integration tests**: pytest + PostgreSQL (when available); test full request/response cycle
- **No test = no code**: TDD Red-Green-Refactor enforced for every change

## Validation

- Project builds and all tests pass before each commit
- Schema migrations tested against both SQLite and PostgreSQL
- First milestone: Customer list/detail view with tests

## Consequences

### Positive

- Direct SQL compatibility with 240 existing Access queries
- Server-rendered HTML matches the Access form-driven UX pattern
- Minimal frontend complexity (no build step, no node_modules)
- SQLAlchemy models serve as living documentation of the data model
- TDD from day one prevents regression

### Negative

- Team must learn Python idioms (mitigated by Java experience transferring well)
- WeasyPrint has system-level dependencies (mitigated by Docker in production)
- SQLite cannot run all PostgreSQL-specific features (mitigated by keeping tests database-agnostic where possible)

### Neutral

- Firebase Authentication adds a Google Cloud dependency
- Cloud Run requires containerization (Dockerfile needed later)

## Monitoring & Rollback

- **Review date**: After first 3 entity modules are complete
- **Success metrics**: All tests pass, schema covers core tables, at least one workflow end-to-end
- **Rollback strategy**: Technology choice is revisable at this stage; no production deployment yet

## References

- Access source exports: `../ith-access-gui/src/access-gui/`
- PostgreSQL DDL: `../ith-access-gui/analysis/metadata/ith_data_schema.sql`
- Workflow map: `../ith-access-gui/docs/workflow-map.md`
- Module index: `../ith-access-gui/docs/module-index.md`
