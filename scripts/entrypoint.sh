#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  sifusherif — Docker entrypoint
#  Runs on every container start before Gunicorn.
# ─────────────────────────────────────────────────────────────
set -e

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[entrypoint] Running database migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Creating superuser (if not already exists)..."
python manage.py create_superuser_env

echo "[entrypoint] Starting Gunicorn..."
exec "$@"
