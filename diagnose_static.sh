#!/bin/bash

# Script de diagnóstico para problemas de archivos estáticos
echo "🔍 Diagnóstico de Archivos Estáticos - OrientandoSAS API"
echo "========================================================="

# Verificar estructura de directorios
echo ""
echo "📁 Verificando estructura de directorios..."
echo "Directorio actual: $(pwd)"
echo "Contenido del directorio app:"
ls -la /app/ 2>/dev/null || ls -la .

echo ""
echo "📁 Verificando directorios estáticos..."
if [ -d "/app/staticfiles" ]; then
    echo "✅ /app/staticfiles existe"
    echo "   Contenido: $(ls -la /app/staticfiles 2>/dev/null | wc -l) archivos"
else
    echo "❌ /app/staticfiles NO existe"
    echo "   Creando directorio..."
    mkdir -p /app/staticfiles
    echo "✅ Directorio creado"
fi

if [ -d "/app/media" ]; then
    echo "✅ /app/media existe"
else
    echo "❌ /app/media NO existe"
    echo "   Creando directorio..."
    mkdir -p /app/media
    echo "✅ Directorio creado"
fi

echo ""
echo "⚙️ Verificando configuración Django..."

# Verificar variables de entorno
echo "Variables de entorno importantes:"
echo "  STATIC_ROOT: ${STATIC_ROOT:-'No definido'}"
echo "  STATIC_URL: ${STATIC_URL:-'No definido'}"
echo "  DEBUG: ${DEBUG:-'No definido'}"

echo ""
echo "🧪 Probando collectstatic..."
python manage.py collectstatic --dry-run --noinput 2>&1 || echo "❌ Error en collectstatic dry-run"

echo ""
echo "📊 Estado de la configuración:"
python manage.py shell -c "
from django.conf import settings
import os

print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'DEBUG: {settings.DEBUG}')

# Verificar si los directorios existen
static_exists = os.path.exists(settings.STATIC_ROOT)
media_exists = os.path.exists(settings.MEDIA_ROOT)

print(f'STATIC_ROOT existe: {static_exists}')
print(f'MEDIA_ROOT existe: {media_exists}')

if not static_exists:
    print(f'Creando STATIC_ROOT: {settings.STATIC_ROOT}')
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)

if not media_exists:
    print(f'Creando MEDIA_ROOT: {settings.MEDIA_ROOT}')
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
"

echo ""
echo "✅ Diagnóstico completado"
echo "========================================================="
