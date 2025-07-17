# 🔧 Solución al Error de Nginx en Dokploy

## ❌ Problema Identificado

```
2025/07/17 08:04:56 [emerg] 1#1: "add_header" directive is not allowed here in /etc/nginx/nginx.conf:55
nginx: [emerg] "add_header" directive is not allowed here in /etc/nginx/nginx.conf:55
```

### Causa:
Las directivas `add_header` de CORS estaban colocadas fuera del contexto correcto en la configuración de Nginx.

## ✅ Soluciones Implementadas

### **Solución 1: Configuración Simplificada (Recomendada para Dokploy)**

**Usar `docker-compose.dokploy.yml` SIN Nginx:**
- ✅ Django sirve directamente en puerto 80
- ✅ CORS configurado en Django (más confiable)
- ✅ Sin problemas de configuración de Nginx
- ✅ Más simple para Dokploy

```yaml
# En docker-compose.dokploy.yml
web:
  ports:
    - "80:8000"  # Django directamente en puerto 80
  # Nginx comentado/deshabilitado
```

### **Solución 2: Configuración Nginx Corregida**

Si prefieres usar Nginx, el `nginx.conf` ha sido corregido:
- ✅ Headers CORS dentro de bloques `location`
- ✅ Directivas `add_header` en contexto correcto
- ✅ Manejo de preflight requests mejorado

## 🚀 Para Desplegar en Dokploy

### **Opción A: Sin Nginx (Más Simple)**
1. Usar archivo: `docker-compose.dokploy.yml`
2. Nginx está comentado/deshabilitado
3. Django sirve directamente en puerto 80
4. CORS manejado por Django

### **Opción B: Con Nginx Corregido**
1. Descomentar el servicio nginx en `docker-compose.dokploy.yml`
2. El archivo `nginx.conf` ya está corregido
3. Django en puerto 8000 interno, Nginx en puerto 80

### **Opción C: Ultra Simple**
Usar el archivo `docker-compose.simple.yml` que es aún más básico.

## 📊 Comparación de Opciones

| Característica | Sin Nginx | Con Nginx Corregido |
|---------------|-----------|-------------------|
| **Simplicidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **CORS** | ✅ Django | ✅ Nginx + Django |
| **Archivos Estáticos** | ✅ Django | ✅ Nginx (mejor) |
| **Performance** | ✅ Buena | ⭐ Mejor |
| **Complejidad** | ✅ Baja | ⚠️ Media |
| **Problemas** | ✅ Menos | ⚠️ Posibles |

## 🔧 Configuración Actual

### **Django CORS (Funciona en ambas opciones):**
```python
# En settings.py
CORS_ALLOW_ALL_ORIGINS = True  # Para desarrollo
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [..., 'X-API-Key', ...]
```

### **Archivos Estáticos:**
```python
# En settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### **URLs configuradas:**
```python
# En urls.py
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 🎯 Recomendación para Dokploy

**Usar la configuración SIN Nginx** porque:
1. ✅ **Menos complejidad** - Un contenedor menos
2. ✅ **Menos problemas** - Sin configuraciones complejas de Nginx
3. ✅ **CORS ya funciona** - Django maneja CORS perfectamente
4. ✅ **Más rápido** - Menos tiempo de configuración
5. ✅ **Fácil debug** - Un solo servicio principal

## 📝 Variables de Entorno para Dokploy

```env
# Esenciales
DJANGO_SECRET_KEY=tu-clave-secreta-segura
DB_PASSWORD=tu-contraseña-segura
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# CORS (opcionales, Django tiene valores por defecto)
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=true

# Base de datos
DB_NAME=orientando_db
DB_USER=orientando_user
DB_HOST=db
DB_PORT=5432
```

## ✅ Resultado Esperado

Después de aplicar la solución:
- ✅ Sin errores de Nginx
- ✅ API accesible en tu dominio
- ✅ CORS funcionando para frontends y n8n
- ✅ Admin Django accesible
- ✅ Documentación API disponible
- ✅ Archivos estáticos servidos correctamente

## 🧪 Probar que Funciona

```bash
# Test básico
curl -X GET "https://tu-dominio.com/api/v1/citas/" \
  -H "X-API-Key: tu-api-key"

# Test CORS desde navegador
fetch('https://tu-dominio.com/api/v1/citas/', {
    headers: {'X-API-Key': 'tu-api-key'}
})
```

¡El problema de Nginx está solucionado! 🎉
