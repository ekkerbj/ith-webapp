# ITH Webapp

Service management webapp replacing the legacy Microsoft Access application.
Built with Python, Flask, and SQLAlchemy.

## Prerequisites

- Python 3.12+
- `virtualenv` (if `python3-venv` is unavailable)

## Setup

```bash
# Create virtual environment
virtualenv .venv

# Activate it
source .venv/bin/activate

# Install the project and dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=ith_webapp
```

## Running the Dev Server

```bash
flask --app src/ith_webapp/app:create_app run --debug
```

## Loading Access Data Locally

```bash
./start.sh
```

`start.sh` uses `sqlite:///ith_import.db` by default. To rebuild that database from the Access source files, run:

```bash
.venv/bin/python -m ith_webapp.commands.import_access --database-url sqlite:///ith_import.db --access-dir access
```

## Project Structure

```
src/ith_webapp/
├── app.py              # Flask app factory
├── database.py         # SQLAlchemy engine/session setup
├── models/             # ORM models
├── repositories/       # Data access layer
├── services/           # Business logic
├── views/              # Flask blueprints (routes)
├── templates/          # Jinja2 templates
└── static/             # CSS, JS, images
```
