#!/bin/bash

# Salir si cualquier comando falla
set -e

echo "⏳ Esperando que la base de datos esté disponible..."
./wait_for_db.sh db

echo "✅ Aplicando migraciones..."
python manage.py migrate

echo "✅ Creando superusuario (si no existe)..."
python backend/create_superuser.py

echo "✅ Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Levantando Gunicorn..."
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
