# 🚀 Guía de Despliegue en Dokploy

## Problemas Solucionados

✅ **Variables de entorno faltantes**
✅ **Red no definida** 
✅ **Versión obsoleta de Docker Compose**
✅ **Configuración optimizada para Dokploy**

## 📋 Pasos para Desplegar en Dokploy

### 1. Configurar Variables de Entorno en Dokploy

En el panel de Dokploy, ve a la sección de **Variables de Entorno** y añade:

```env
# Django Configuration
DJANGO_SECRET_KEY=tu-clave-secreta-super-segura-de-produccion
DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos PostgreSQL
DB_NAME=orientando_db
DB_USER=orientando_user
DB_PASSWORD=tu-contraseña-super-segura
DB_HOST=db
DB_PORT=5432
```

### 2. Seleccionar el Archivo Docker Compose Correcto

En Dokploy, usa uno de estos archivos según tus necesidades:

**Opción A: Para uso con Dokploy (Recomendado)**
```
docker-compose.dokploy.yml
```

**Opción B: Combinación de archivos**
```
docker-compose.yml + docker-compose.prod.yml
```

### 3. Configuraciones Específicas para Dokploy

#### Variables de Entorno Obligatorias:
- `DJANGO_SECRET_KEY` - Clave secreta de Django
- `DB_PASSWORD` - Contraseña de PostgreSQL
- `DJANGO_ALLOWED_HOSTS` - Dominios permitidos

#### Configuración de Red:
- Usamos `app_network` (compatible con Dokploy)
- Eliminamos la versión obsoleta de Docker Compose

#### Puertos:
- Puerto 80 y 443 para Nginx
- Puerto 8000 interno para Django (no expuesto)
- Puerto 5432 interno para PostgreSQL (no expuesto)

## 🔧 Archivos Optimizados para Dokploy

### `docker-compose.dokploy.yml`
- ✅ Sin versión obsoleta
- ✅ Variables con valores por defecto
- ✅ Red compatible con Dokploy
- ✅ Healthchecks optimizados

### Variables con Fallbacks
```yaml
environment:
  SECRET_KEY: ${DJANGO_SECRET_KEY:-valor-por-defecto}
  DB_PASSWORD: ${DB_PASSWORD:-orientando_pass123}
```

## 🚨 Checklist Pre-Despliegue

- [ ] Variables de entorno configuradas en Dokploy
- [ ] Dominio apuntando al servidor
- [ ] Certificado SSL configurado (opcional)
- [ ] Archivo `docker-compose.dokploy.yml` seleccionado

## 🔐 Configuración de Seguridad para Producción

### 1. Generar Nueva Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. Variables de Entorno Seguras
```env
DJANGO_SECRET_KEY=nueva-clave-super-segura-de-50-caracteres
DB_PASSWORD=contraseña-muy-segura-con-simbolos-123!
DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com
```

## 📊 Monitoreo y Logs

### Ver logs en Dokploy:
1. Ve a la sección de **Logs**
2. Selecciona el servicio (web, db, nginx)
3. Revisa los logs en tiempo real

### Comandos útiles en Dokploy terminal:
```bash
# Ver estado de contenedores
docker ps

# Ver logs específicos
docker logs orientando_web
docker logs orientando_db

# Ejecutar comandos Django
docker exec orientando_web python manage.py migrate
docker exec orientando_web python manage.py createsuperuser
```

## 🆘 Solución de Problemas Comunes

### Error: "DJANGO_SECRET_KEY variable is not set"
**Solución**: Configurar la variable en el panel de Dokploy

### Error: "service refers to undefined network"
**Solución**: Usar `docker-compose.dokploy.yml`

### Error: "version is obsolete"
**Solución**: Los nuevos archivos no incluyen la versión

### Error de conexión a PostgreSQL
**Solución**: Verificar variables `DB_*` en Dokploy

## 🎯 Configuración Final Recomendada

### En Dokploy Panel:
1. **Repositorio**: Tu repo de GitHub
2. **Archivo Docker Compose**: `docker-compose.dokploy.yml`
3. **Variables de Entorno**: Todas las mencionadas arriba
4. **Dominio**: Configurar tu dominio personalizado
5. **SSL**: Activar certificado automático

### Resultado Esperado:
- ✅ API accesible en tu dominio
- ✅ Admin Django funcionando
- ✅ Base de datos PostgreSQL conectada
- ✅ Archivos estáticos servidos por Nginx
- ✅ HTTPS automático (si está configurado)

¡Tu API de OrientandoSAS debería desplegarse correctamente en Dokploy! 🎉
