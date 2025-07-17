#!/bin/bash

# Script de verificación para despliegue en Dokploy
echo "🔍 Verificando configuración para Dokploy..."

# Verificar archivos necesarios
echo "📁 Verificando archivos..."
files_to_check=(
    "Dockerfile"
    "docker-compose.dokploy.yml"
    "nginx.conf"
    "requirements.txt"
    "manage.py"
    ".env.production"
)

missing_files=()
for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    else
        echo "✅ $file - OK"
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Archivos faltantes:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Verificar configuración de Django
echo ""
echo "⚙️ Verificando configuración Django..."

# Verificar settings.py
if grep -q "ALLOWED_HOSTS" config/settings.py; then
    echo "✅ ALLOWED_HOSTS configurado"
else
    echo "❌ ALLOWED_HOSTS no encontrado en settings.py"
fi

if grep -q "DATABASES" config/settings.py; then
    echo "✅ DATABASES configurado"
else
    echo "❌ DATABASES no encontrado en settings.py"
fi

# Verificar variables de entorno requeridas
echo ""
echo "🔐 Variables de entorno requeridas para Dokploy:"
echo "   DJANGO_SECRET_KEY=tu-clave-secreta"
echo "   DB_PASSWORD=tu-contraseña-segura"
echo "   DJANGO_ALLOWED_HOSTS=tu-dominio.com"
echo "   DEBUG=False"

# Verificar docker-compose.dokploy.yml
echo ""
echo "🐳 Verificando docker-compose.dokploy.yml..."
if grep -q "app_network" docker-compose.dokploy.yml; then
    echo "✅ Red app_network configurada"
else
    echo "❌ Red app_network no encontrada"
fi

if grep -q "DJANGO_SECRET_KEY" docker-compose.dokploy.yml; then
    echo "✅ Variables de entorno configuradas"
else
    echo "❌ Variables de entorno no configuradas"
fi

# Verificar puertos en nginx
echo ""
echo "🌐 Verificando configuración Nginx..."
if grep -q "listen 80" nginx.conf; then
    echo "✅ Puerto 80 configurado"
else
    echo "❌ Puerto 80 no configurado"
fi

if grep -q "proxy_pass.*web:8000" nginx.conf; then
    echo "✅ Proxy a Django configurado"
else
    echo "❌ Proxy a Django no configurado"
fi

echo ""
echo "🎯 Configuración lista para Dokploy!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Subir código a GitHub"
echo "2. Crear proyecto en Dokploy"
echo "3. Seleccionar docker-compose.dokploy.yml"
echo "4. Configurar variables de entorno en Dokploy"
echo "5. Desplegar"
echo ""
echo "📖 Ver DOKPLOY_GUIDE.md para instrucciones detalladas"
