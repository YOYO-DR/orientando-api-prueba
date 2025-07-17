#!/bin/bash

echo "=== VERIFICACIÓN DE ARCHIVOS ESTÁTICOS PARA DOKPLOY ==="
echo

# Verificar estructura de directorios
echo "1. Verificando estructura de directorios..."
ls -la /app/
echo

echo "2. Verificando directorio staticfiles..."
if [ -d "/app/staticfiles" ]; then
    echo "✅ /app/staticfiles existe"
    echo "Contenido del directorio staticfiles:"
    ls -la /app/staticfiles/
    echo
    
    if [ -d "/app/staticfiles/admin" ]; then
        echo "✅ /app/staticfiles/admin existe"
        echo "Contenido del directorio admin:"
        ls -la /app/staticfiles/admin/
        echo
        
        # Verificar archivos específicos
        FILES_TO_CHECK=(
            "/app/staticfiles/admin/css/base.css"
            "/app/staticfiles/admin/css/login.css"
            "/app/staticfiles/admin/js/theme.js"
            "/app/staticfiles/admin/js/nav_sidebar.js"
        )
        
        echo "3. Verificando archivos críticos del admin:"
        for file in "${FILES_TO_CHECK[@]}"; do
            if [ -f "$file" ]; then
                size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
                echo "✅ $file - $size bytes"
            else
                echo "❌ $file - NO ENCONTRADO"
            fi
        done
    else
        echo "❌ /app/staticfiles/admin NO existe"
    fi
else
    echo "❌ /app/staticfiles NO existe"
fi

echo
echo "4. Ejecutando collectstatic manualmente..."
python manage.py collectstatic --noinput --clear --verbosity=2

echo
echo "5. Verificando después de collectstatic..."
if [ -d "/app/staticfiles/admin" ]; then
    echo "✅ Admin static files recolectados correctamente"
    echo "Total de archivos admin:"
    find /app/staticfiles/admin -type f | wc -l
else
    echo "❌ Archivos admin NO recolectados"
fi

echo
echo "6. Verificando configuración de Django..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'DEBUG: {settings.DEBUG}')
"

echo
echo "=== FIN DE VERIFICACIÓN ==="
