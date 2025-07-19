#!/bin/bash
set -e

# Esperar a que PostgreSQL esté disponible
./wait-for-postgres.sh db 5432

# Crear directorios si no existen
echo "Creando directorios necesarios..."
mkdir -p /app/staticfiles
mkdir -p /app/media
mkdir -p /app/logs

# Ejecutar migraciones
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe
echo "Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User;
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@orientando.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Iniciar servidor
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000
