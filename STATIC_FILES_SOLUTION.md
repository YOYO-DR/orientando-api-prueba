# Solución para Archivos Estáticos en Dokploy

## Problema Identificado
Los archivos estáticos del admin de Django (CSS/JS) no se están sirviendo correctamente, causando errores de MIME type y 404.

## Cambios Realizados

### 1. Agregado WhiteNoise
- ✅ Agregado `whitenoise==6.8.2` a `requirements.txt`
- ✅ Configurado WhiteNoise middleware en `settings.py`
- ✅ Configurado `STATICFILES_STORAGE` para comprimir archivos

### 2. Corregido docker-compose.dokploy.yml
- ✅ Habilitado puerto `8000:8000` para Dokploy
- ✅ Agregado dominio `orien-prueba.yoyodr.dev` a `ALLOWED_HOSTS`
- ✅ Corregido variables de entorno para DB (valores fijos en lugar de variables)
- ✅ Agregado logging detallado en el comando de inicio
- ✅ Agregado verificación de archivos estáticos

### 3. Simplificado URLs
- ✅ Removido condicional DEBUG para servir archivos estáticos
- ✅ Django sirve archivos estáticos siempre (sin Nginx)

### 4. Scripts de Diagnóstico
- ✅ Creado `debug_static.py` para diagnóstico local
- ✅ Creado `check_static_files.sh` para verificación en contenedor

## Pasos para Resolver

### 1. Reconstruir Imagen Docker
```bash
docker-compose -f docker-compose.dokploy.yml build --no-cache
```

### 2. Verificar Configuración Local
```bash
python debug_static.py
```

### 3. Desplegar en Dokploy
```bash
docker-compose -f docker-compose.dokploy.yml up -d
```

### 4. Verificar Logs
```bash
docker-compose -f docker-compose.dokploy.yml logs web
```

### 5. Verificar Archivos Estáticos en Contenedor
```bash
docker-compose -f docker-compose.dokploy.yml exec web ./check_static_files.sh
```

## URLs de Verificación
- Admin: `https://orien-prueba.yoyodr.dev/admin/`
- API Docs: `https://orien-prueba.yoyodr.dev/api/docs/`
- Archivo CSS: `https://orien-prueba.yoyodr.dev/static/admin/css/base.css`

## Configuración Clave

### WhiteNoise en settings.py
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # IMPORTANTE
    # ... otros middlewares
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'orien-prueba.yoyodr.dev']
```

## Comando de Inicio Mejorado
El comando ahora incluye:
1. Verificación de directorios
2. Migraciones
3. Recolección de archivos estáticos con logging
4. Verificación de archivos críticos
5. Inicio de Gunicorn

## Notas Importantes
- ✅ Sin Nginx: Django maneja archivos estáticos directamente
- ✅ WhiteNoise: Optimiza el servicio de archivos estáticos
- ✅ Puerto 8000: Expuesto para Dokploy
- ✅ Variables de entorno: Configuradas correctamente
