#!/bin/sh

# Ejecuta las migraciones de la base de datos
echo "Applying database migrations..."
python manage.py migrate

# Ejecuta el seeder (opcional, coméntalo si no quieres que se ejecute en cada reinicio)
echo "Seeding database..."
python manage.py seed_db

# Inicia el servidor Gunicorn
echo "Starting Gunicorn server..."
gunicorn centavo.wsgi --bind 0.0.0.0:8000
