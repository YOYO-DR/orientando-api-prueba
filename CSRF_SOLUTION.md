# Solución para Error CSRF - Dokploy

## Problema
```
Forbidden (403)
CSRF verification failed. Request aborted.
More information is available with DEBUG=True.
```

## ✅ Solución Implementada

### 1. Configuración CSRF en settings.py
```python
# Dominios confiables para CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://orien-prueba.yoyodr.dev',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Configuración adicional de CSRF para producción
CSRF_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript si es necesario
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'

# Headers de CSRF
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# Configuración de sesiones para CSRF
SESSION_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### 2. Docker Compose Corregido
- ✅ Agregado servicio PostgreSQL que faltaba
- ✅ Puerto 8000:8000 habilitado
- ✅ Variables de entorno DB corregidas (valores fijos)
- ✅ ALLOWED_HOSTS incluye el dominio de Dokploy

### 3. CORS Headers
Ya configurado en CORS_ALLOW_HEADERS:
```python
'x-csrftoken',  # Importante para CSRF
```

## 🚀 Pasos para Aplicar

### 1. Rebuild y Deploy
```bash
# En Dokploy o local
docker-compose -f docker-compose.dokploy.yml build --no-cache
docker-compose -f docker-compose.dokploy.yml up -d
```

### 2. Verificar Variables de Entorno en Dokploy
Asegurar que estén configuradas:
- `DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,orien-prueba.yoyodr.dev`
- Variables de DB según corresponda

### 3. Verificar Logs
```bash
docker-compose -f docker-compose.dokploy.yml logs web
```

### 4. Test del Admin
1. Ir a: `https://orien-prueba.yoyodr.dev/admin/`
2. Debería cargar sin errores CSRF
3. Login debería funcionar correctamente

## 🔧 Si Persiste el Error

### Opción 1: Verificar el Dominio
Asegurar que el dominio en `CSRF_TRUSTED_ORIGINS` sea exactamente el mismo que usa Dokploy.

### Opción 2: Debug Temporal
Cambiar temporalmente `DEBUG=True` para ver más detalles del error.

### Opción 3: Verificar HTTPS
Dokploy maneja HTTPS automáticamente. La configuración:
- `CSRF_COOKIE_SECURE = not DEBUG` se adapta automáticamente
- En producción (DEBUG=False) → cookies seguras (HTTPS)
- En desarrollo (DEBUG=True) → cookies normales (HTTP)

## 📝 Notas Importantes

1. **CSRF_TRUSTED_ORIGINS**: Es la configuración clave que resuelve el problema
2. **WhiteNoise**: Mantiene archivos estáticos funcionando
3. **PostgreSQL**: Ahora incluido correctamente en docker-compose
4. **CORS**: Ya configurado para API calls desde frontend/n8n

## ✅ Estado Final
- ✅ Archivos estáticos: Funcionando
- ✅ CSRF: Configurado para Dokploy
- ✅ Base de datos: PostgreSQL incluida
- ✅ CORS: Configurado para APIs
- ✅ Despliegue: Listo para Dokploy
