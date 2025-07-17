#!/usr/bin/env python
"""
Script para diagnosticar problemas con archivos estáticos en Django
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find

def debug_static_files():
    print("=== DIAGNÓSTICO DE ARCHIVOS ESTÁTICOS ===\n")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print()
    
    # Verificar que el directorio STATIC_ROOT existe
    if os.path.exists(settings.STATIC_ROOT):
        print(f"✅ STATIC_ROOT existe: {settings.STATIC_ROOT}")
        
        # Listar contenido
        static_files = []
        for root, dirs, files in os.walk(settings.STATIC_ROOT):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), settings.STATIC_ROOT)
                static_files.append(rel_path)
        
        print(f"📁 Total de archivos estáticos: {len(static_files)}")
        
        # Verificar archivos específicos del admin
        admin_files = [f for f in static_files if f.startswith('admin/')]
        print(f"📁 Archivos del admin: {len(admin_files)}")
        
        # Buscar archivos específicos problemáticos
        problem_files = [
            'admin/css/base.css',
            'admin/css/login.css',
            'admin/js/theme.js',
            'admin/js/nav_sidebar.js'
        ]
        
        print("\n=== ARCHIVOS CRÍTICOS DEL ADMIN ===")
        for file in problem_files:
            full_path = os.path.join(settings.STATIC_ROOT, file)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"✅ {file} - {size} bytes")
            else:
                print(f"❌ {file} - NO ENCONTRADO")
                
                # Intentar buscar con finder
                found = find(file)
                if found:
                    print(f"   🔍 Encontrado en: {found}")
                else:
                    print(f"   🔍 No encontrado por Django finder")
        
        print("\n=== ALGUNOS ARCHIVOS DEL ADMIN ===")
        admin_sample = [f for f in admin_files if any(ext in f for ext in ['.css', '.js'])][:10]
        for file in admin_sample:
            print(f"  {file}")
            
    else:
        print(f"❌ STATIC_ROOT no existe: {settings.STATIC_ROOT}")
    
    print(f"\n=== CONFIGURACIÓN DE MEDIA ===")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    if os.path.exists(settings.MEDIA_ROOT):
        print(f"✅ MEDIA_ROOT existe: {settings.MEDIA_ROOT}")
    else:
        print(f"❌ MEDIA_ROOT no existe: {settings.MEDIA_ROOT}")

if __name__ == '__main__':
    debug_static_files()
