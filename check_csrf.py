#!/usr/bin/env python
"""
Script para verificar configuración CSRF en Django
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def check_csrf_config():
    print("=== VERIFICACIÓN DE CONFIGURACIÓN CSRF ===\n")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print()
    
    # Verificar CSRF_TRUSTED_ORIGINS
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print("✅ CSRF_TRUSTED_ORIGINS configurado:")
        for origin in settings.CSRF_TRUSTED_ORIGINS:
            print(f"  - {origin}")
    else:
        print("❌ CSRF_TRUSTED_ORIGINS NO configurado")
    print()
    
    # Verificar configuración de cookies CSRF
    print("=== CONFIGURACIÓN DE COOKIES CSRF ===")
    print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'No configurado')}")
    print(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'No configurado')}")
    print(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'No configurado')}")
    print(f"CSRF_COOKIE_NAME: {getattr(settings, 'CSRF_COOKIE_NAME', 'No configurado')}")
    print()
    
    # Verificar configuración de sesiones
    print("=== CONFIGURACIÓN DE SESIONES ===")
    print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'No configurado')}")
    print(f"SESSION_COOKIE_HTTPONLY: {getattr(settings, 'SESSION_COOKIE_HTTPONLY', 'No configurado')}")
    print(f"SESSION_COOKIE_SAMESITE: {getattr(settings, 'SESSION_COOKIE_SAMESITE', 'No configurado')}")
    print()
    
    # Verificar middleware CSRF
    print("=== MIDDLEWARE CSRF ===")
    if 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE:
        csrf_index = settings.MIDDLEWARE.index('django.middleware.csrf.CsrfViewMiddleware')
        print(f"✅ CsrfViewMiddleware encontrado en posición {csrf_index}")
        print("Middlewares antes del CSRF:")
        for i, middleware in enumerate(settings.MIDDLEWARE[:csrf_index]):
            print(f"  {i}: {middleware}")
    else:
        print("❌ CsrfViewMiddleware NO encontrado en MIDDLEWARE")
    print()
    
    # Verificar CORS headers
    print("=== CONFIGURACIÓN CORS PARA CSRF ===")
    if hasattr(settings, 'CORS_ALLOW_HEADERS'):
        if 'x-csrftoken' in settings.CORS_ALLOW_HEADERS:
            print("✅ x-csrftoken permitido en CORS_ALLOW_HEADERS")
        else:
            print("❌ x-csrftoken NO encontrado en CORS_ALLOW_HEADERS")
            
        if 'x-requested-with' in settings.CORS_ALLOW_HEADERS:
            print("✅ x-requested-with permitido en CORS_ALLOW_HEADERS")
        else:
            print("❌ x-requested-with NO encontrado en CORS_ALLOW_HEADERS")
    else:
        print("❌ CORS_ALLOW_HEADERS no configurado")
    print()
    
    # Verificar variables de entorno importantes
    print("=== VARIABLES DE ENTORNO ===")
    print(f"DEBUG (env): {os.getenv('DEBUG', 'No configurado')}")
    print(f"ALLOWED_HOSTS (env): {os.getenv('DJANGO_ALLOWED_HOSTS', 'No configurado')}")
    print(f"SECRET_KEY configurado: {'✅ Sí' if settings.SECRET_KEY else '❌ No'}")
    print()
    
    print("=== RECOMENDACIONES ===")
    
    if not hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print("⚠️  Agregar CSRF_TRUSTED_ORIGINS con el dominio de Dokploy")
    
    if settings.DEBUG:
        print("⚠️  DEBUG=True en producción puede ser inseguro")
    
    if 'orien-prueba.yoyodr.dev' not in str(settings.ALLOWED_HOSTS):
        print("⚠️  Agregar dominio de Dokploy a ALLOWED_HOSTS")
    
    print("\n=== FIN DE VERIFICACIÓN ===")

if __name__ == '__main__':
    check_csrf_config()
