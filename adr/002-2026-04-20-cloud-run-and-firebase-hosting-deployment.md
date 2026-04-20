# ADR 002: Cloud Run and Firebase Hosting Deployment

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Production containerization, static asset delivery, minimal operational complexity, Cloud Run compatibility
- **Tags**: architecture, deployment, cloud-run, firebase-hosting, docker, cloud-build

## Decision

Deploy the Flask application to **Cloud Run** using a container image built from a repository `Dockerfile`. Serve static assets from **Firebase Hosting** and rewrite all dynamic requests to the Cloud Run service.

## Context

The application is a server-rendered Flask system with a small static asset footprint. Cloud Run provides a simple managed runtime for the backend, while Firebase Hosting can serve the public static files with low latency and route application requests to the container.

The runtime also needs a production WSGI server and PostgreSQL support so the container can run outside the development/test SQLite setup.

## Alternatives Considered

### Flask development server in Cloud Run

- **Rejected**: not appropriate for production traffic handling.

### Firebase Hosting only

- **Rejected**: Firebase Hosting cannot run the Flask backend.

### App Engine

- **Rejected**: adds a different operational model without a clear benefit over Cloud Run for this app.

### GitHub Actions for deployment

- **Rejected**: Cloud Build keeps build and deploy steps close to Google Cloud and reduces external CI dependencies.

## Implementation Details

- `Dockerfile` installs the package from `pyproject.toml` and starts `gunicorn` on `$PORT`.
- `src/ith_webapp/wsgi.py` exposes `app = create_app()` for the container entrypoint.
- `pyproject.toml` adds `gunicorn` and `psycopg[binary]` so the production image can serve Flask and connect to PostgreSQL.
- `firebase.json` serves `src/ith_webapp/static` content and rewrites all other routes to the Cloud Run service.
- `cloudbuild.yaml` builds and pushes the image, then deploys the Cloud Run service.

## Validation

- Added repository tests that assert the deployment artifacts and production dependencies are present.
- Full test suite passes after the deployment files were added.

## Consequences

### Positive

- Clear separation between static delivery and backend execution.
- Containerized runtime matches Cloud Run expectations.
- Production dependency support is explicit in packaging.

### Negative

- One static asset path is now deployment-aware.
- Deployment now depends on Google Cloud and Firebase configuration files in the repository.

### Neutral

- Local development still uses the existing Flask factory and SQLite defaults.

## Monitoring & Rollback

- **Review date**: After the first Cloud Run deployment
- **Success metrics**: container starts successfully, static files serve from Firebase Hosting, dynamic routes reach Cloud Run
- **Rollback strategy**: revert the deployment files and redeploy the previous image/configuration

## References

- `Dockerfile`
- `cloudbuild.yaml`
- `firebase.json`
- `src/ith_webapp/wsgi.py`
- `pyproject.toml`
- ADR 001: Technology Selection
