#!/usr/bin/env bash
.venv/bin/alembic upgrade head
exec env SECRET_KEY='replace-with-a-long-random-secret' FIREBASE_API_KEY='AIzaSyCh1qIUEsP1S60xqR-4cJFCHyhS-_OOeWg' DATABASE_URL="${DATABASE_URL:-sqlite:///ith.db}" FLASK_DEBUG=1 .venv/bin/python -m flask --app src/ith_webapp/app:create_app run --debug --host 127.0.0.1 --port 5000
