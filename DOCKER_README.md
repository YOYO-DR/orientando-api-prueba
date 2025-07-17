# Docker Setup para OrientandoSAS API

Este proyecto incluye configuración completa de Docker para desarrollo y producción.

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker
- Docker Compose

### Desarrollo

1. **Clonar y configurar el proyecto:**
```bash
cd "OrientandoSAS API Django"
cp .env.docker.example .env.docker
```

2. **Iniciar los servicios:**
```bash
docker-compose up -d
```

3. **Acceder a la aplicación:**
- API: http://localhost:8000
- Admin Django: http://localhost:8000/admin/ (admin/admin123)
- Documentación API: http://localhost:8000/api/schema/swagger-ui/
- Adminer (DB): http://localhost:8080

### Comandos Útiles

**Ver logs:**
```bash
docker-compose logs -f web
docker-compose logs -f db
```

**Ejecutar comandos Django:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic
```

**Acceder al contenedor:**
```bash
docker-compose exec web bash
docker-compose exec db psql -U orientando_user -d orientando_db
```

**Detener servicios:**
```bash
docker-compose down
```

**Reiniciar servicios:**
```bash
docker-compose restart
```

**Limpiar todo (⚠️ ELIMINA DATOS):**
```bash
docker-compose down -v
docker system prune -f
```

## 🏭 Producción

### Configuración de producción:

1. **Crear archivo de entorno:**
```bash
cp .env.docker.example .env.production
```

2. **Editar variables críticas en .env.production:**
```env
DEBUG=False
DJANGO_SECRET_KEY=tu-clave-super-segura-de-produccion
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DB_PASSWORD=contraseña-muy-segura
```

3. **Iniciar en modo producción:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### Características de Producción:
- ✅ Nginx como proxy reverso
- ✅ Gunicorn como servidor WSGI
- ✅ Configuración de seguridad
- ✅ Compresión Gzip
- ✅ Manejo de archivos estáticos
- ✅ SSL/TLS ready

## 📊 Servicios

### Desarrollo:
- **web**: Django con servidor de desarrollo
- **db**: PostgreSQL 15
- **adminer**: Interfaz web para DB

### Producción:
- **nginx**: Proxy reverso y archivos estáticos
- **web**: Django con Gunicorn
- **db**: PostgreSQL optimizado

## 🗄️ Base de Datos

**Conexión desde aplicaciones externas:**
- Host: localhost
- Puerto: 5432
- Database: orientando_db
- Usuario: orientando_user
- Contraseña: orientando_pass123

## 📁 Volúmenes

- `postgres_data`: Datos de PostgreSQL (persistente)
- `static_volume`: Archivos estáticos de Django
- `media_volume`: Archivos de media

## 🔧 Personalización

### Configurar SSL/HTTPS:
1. Colocar certificados en `./ssl/`
2. Descomentar configuración HTTPS en `nginx.conf`
3. Usar `docker-compose.prod.yml`

### Cambiar puertos:
Editar `docker-compose.yml` o usar variables de entorno:
```yaml
ports:
  - "${WEB_PORT:-8000}:8000"
```

### Configurar backup automático:
```bash
# Backup manual
docker-compose exec db pg_dump -U orientando_user orientando_db > backup.sql

# Restaurar
docker-compose exec -T db psql -U orientando_user orientando_db < backup.sql
```

## 🚨 Troubleshooting

**Error de permisos:**
```bash
sudo chown -R $USER:$USER .
```

**Puerto ocupado:**
```bash
docker-compose down
sudo lsof -i :8000
```

**Reiniciar desde cero:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**Ver estado de servicios:**
```bash
docker-compose ps
docker-compose top
```

## 📚 Estructura de Archivos Docker

```
├── Dockerfile                 # Imagen de Django
├── docker-compose.yml        # Configuración base
├── docker-compose.override.yml  # Desarrollo
├── docker-compose.prod.yml   # Producción
├── .dockerignore             # Archivos a ignorar
├── nginx.conf                # Configuración Nginx
├── .env.docker.example       # Variables de entorno ejemplo
└── DOCKER_README.md          # Este archivo
```

## 🔐 Seguridad

Para producción:
- ✅ Cambiar todas las contraseñas por defecto
- ✅ Usar `DEBUG=False`
- ✅ Configurar `ALLOWED_HOSTS` específicos
- ✅ Generar nueva `SECRET_KEY`
- ✅ Usar HTTPS con certificados válidos
- ✅ Configurar firewall
- ✅ Actualizar imagen base regularmente

¡Tu API de OrientandoSAS está lista para correr en Docker! 🐳
