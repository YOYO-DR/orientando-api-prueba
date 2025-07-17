# Configuración para PostgreSQL Externo en Dokploy

## 🎯 Objetivo
Configurar la aplicación Django para usar PostgreSQL externo gestionado por Dokploy y variables de entorno para CSRF.

## ✅ Cambios Realizados

### 1. CSRF_TRUSTED_ORIGINS como Variable de Entorno

**En settings.py:**
```python
# Dominios confiables para CSRF (desde variable de entorno)
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 
    'https://orien-prueba.yoyodr.dev,http://localhost:8000,http://127.0.0.1:8000'
).split(',')
```

**En docker-compose.dokploy.yml:**
```yaml
environment:
  CSRF_TRUSTED_ORIGINS: ${CSRF_TRUSTED_ORIGINS:-https://orien-prueba.yoyodr.dev,http://localhost:8000,http://127.0.0.1:8000}
```

### 2. PostgreSQL Externo

**Removido del docker-compose:**
- ❌ Servicio `db` PostgreSQL interno
- ❌ Volumen `postgres_data`
- ❌ Dependencias internas de BD

**Variables de BD ahora requieren configuración externa:**
```yaml
DB_NAME: ${DB_NAME}        # Sin valor por defecto
DB_USER: ${DB_USER}        # Sin valor por defecto  
DB_PASSWORD: ${DB_PASSWORD}# Sin valor por defecto
DB_HOST: ${DB_HOST}        # Sin valor por defecto
DB_PORT: ${DB_PORT:-5432}  # Puerto por defecto 5432
```

### 3. Puerto Expuesto
```yaml
ports:
  - "8000:8000"  # Expuesto para Dokploy
```

## 🚀 Configuración en Dokploy

### Variables de Entorno Requeridas:

1. **Django:**
   ```
   DEBUG=False
   DJANGO_SECRET_KEY=tu_clave_secreta_segura
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
   ```

2. **CSRF:**
   ```
   CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,http://localhost:8000
   ```

3. **Base de Datos (PostgreSQL externo):**
   ```
   DB_NAME=nombre_de_tu_bd
   DB_USER=usuario_de_tu_bd
   DB_PASSWORD=password_de_tu_bd
   DB_HOST=host_de_tu_bd_postgres
   DB_PORT=5432
   ```

### Ejemplo de Configuración Completa:
```
DEBUG=False
DJANGO_SECRET_KEY=django-super-secret-key-123456789
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,orien-prueba.yoyodr.dev
CSRF_TRUSTED_ORIGINS=https://orien-prueba.yoyodr.dev
DB_NAME=orientando_production
DB_USER=orientando_user
DB_PASSWORD=super_secure_password_123
DB_HOST=postgres.tu-servidor.com
DB_PORT=5432
```

## 📝 Ventajas de esta Configuración

1. **🔒 Seguridad:** PostgreSQL gestionado externamente por Dokploy
2. **⚡ Rendimiento:** Sin contenedor BD interno
3. **🔧 Flexibilidad:** CSRF configurable por entorno
4. **📊 Escalabilidad:** BD externa permite mejor gestión
5. **🛡️ Backup:** BD gestionada profesionalmente

## 🔍 Verificación

### 1. Comprobar Variables de Entorno:
```bash
# En el contenedor
echo $CSRF_TRUSTED_ORIGINS
echo $DB_HOST
echo $DB_NAME
```

### 2. Test de Conexión BD:
```bash
# En el contenedor
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT version()')
print('PostgreSQL conectado:', cursor.fetchone()[0])
"
```

### 3. Test de CSRF:
- Ir a `/admin/`
- Verificar que no hay errores CSRF
- Login debe funcionar correctamente

## 🚨 Problemas Comunes

### Error: "No module named 'psycopg2'"
**Solución:** Ya incluido en requirements.txt

### Error: "FATAL: database does not exist"
**Solución:** Verificar variables DB_* en Dokploy

### Error: "CSRF verification failed"
**Solución:** Verificar CSRF_TRUSTED_ORIGINS incluye tu dominio

### Error: "Connection refused"
**Solución:** Verificar DB_HOST y DB_PORT correctos

## 📋 Checklist de Despliegue

- [ ] Configurar PostgreSQL externo en Dokploy
- [ ] Configurar todas las variables de entorno
- [ ] Hacer build de la imagen Docker
- [ ] Desplegar con docker-compose.dokploy.yml
- [ ] Verificar conexión a BD
- [ ] Verificar que admin funciona sin errores CSRF
- [ ] Test de API endpoints

## 🎉 Estado Final

✅ **Aplicación Django:** Lista para PostgreSQL externo  
✅ **CSRF:** Configurable por variable de entorno  
✅ **Archivos estáticos:** WhiteNoise funcionando  
✅ **API:** Lista para uso con frontend/n8n  
✅ **Despliegue:** Optimizado para Dokploy
