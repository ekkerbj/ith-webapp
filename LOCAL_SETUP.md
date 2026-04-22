# Local Setup

This project is a Flask app that uses SQLite for local development and tests by default.

## Prerequisites

- Python 3.12+
- `virtualenv` if `python3-venv` is unavailable

## Install

```bash
virtualenv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Locally

```bash
flask --app src/ith_webapp/app:create_app run --debug
```

For the imported Access dataset, use:

```bash
./start.sh
```

To refresh `ith_import.db` from the Access files:

```bash
.venv/bin/python -m ith_webapp.commands.import_access --database-url sqlite:///ith_import.db --access-dir access
```

Notes:

- The default local database for `start.sh` is SQLite at `sqlite:///ith_import.db`.
- Tables are created automatically on startup.
- Set `DATABASE_URL` if you want to point the app at another database.
- Set `FIREBASE_API_KEY` only if you want to use the real login flow.

## Firebase Local Auth

If you want to test the real Firebase login flow locally, set:

```bash
export SECRET_KEY='replace-with-a-long-random-secret'
export FIREBASE_API_KEY='AIza...'
export DATABASE_URL='sqlite:///ith.db'
export FLASK_DEBUG=1
```

Then create a test user in Firebase Authentication with Email/Password enabled and log in at `/login`.

No-cost Firebase setup used by this app:

- Firebase Authentication
- One Web app for API config

## Test

```bash
pytest
```

With coverage:

```bash
pytest --cov=ith_webapp
```

## Migrations

If schema migrations need to be applied locally:

```bash
alembic upgrade head
```

## Docker

Build and run the container locally:

```bash
docker build -t ith-webapp .
docker run -p 8080:8080 -e PORT=8080 ith-webapp
```
