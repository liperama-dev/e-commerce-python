#!/bin/sh
# entrypoint.sh — runs Alembic migrations then starts the server.
# This ensures the DB schema is always up-to-date on container start.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
