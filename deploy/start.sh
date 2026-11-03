#!/usr/bin/env bash
set -euo pipefail

# Exclusivo de Meritum-SENA. Nunca apuntar a una base institucional.
python manage.py check
python manage.py migrate --noinput
python manage.py preparar_demo_online

# Un trabajador sin hilos evita bloqueos de escritura SQLite durante la exposición.
# También reduce consumo de RAM en la instancia gratuita de Render.
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 1 \
  --threads 1 \
  --timeout 90 \
  --access-logfile -
