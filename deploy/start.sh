#!/usr/bin/env bash
set -euo pipefail

# La base DATABASE_URL es exclusiva de Meritum-SENA. No usar la base institucional.
python manage.py migrate --noinput
python manage.py preparar_demo_online
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --workers 2 --timeout 60 --access-logfile -
