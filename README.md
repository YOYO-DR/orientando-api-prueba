# OrientandoSAS API Django

API REST para el sistema de gestión de citas de OrientandoSAS, desarrollada con Django y Django REST Framework.

## Características

- Django REST Framework para APIs
- PostgreSQL como base de datos
- Documentación automática con drf-spectacular
- Variables de entorno con python-dotenv
- Autenticación y permisos configurados

## Requisitos Previos

- Python 3.12+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## Configuración del Proyecto

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd "OrientandoSAS API Django"
```

### 2. Crear y activar entorno virtual
```bash
python -m venv env
# En Windows:
env\Scripts\activate
# En macOS/Linux:
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

#### Instalar PostgreSQL:
- Descarga e instala PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/)
- Durante la instalación, recuerda la contraseña que estableces para el usuario `postgres`

#### Crear la base de datos:
```sql
-- Conectarse a PostgreSQL como superusuario
psql -U postgres

-- Crear la base de datos
CREATE DATABASE orientando_db;

-- Crear un usuario específico (opcional)
CREATE USER tu_usuario_postgres WITH PASSWORD 'tu_contraseña_postgres';
GRANT ALL PRIVILEGES ON DATABASE orientando_db TO tu_usuario_postgres;

-- Salir
\q
```

### 5. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura tus variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus datos reales:

```env
# Database Configuration
DB_NAME=orientando_db
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Ejecutar migraciones
```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

## Acceder a la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **API Base**: http://localhost:8000/api/v1/
- **Documentación Swagger**: http://localhost:8000/api/docs/
- **Documentación ReDoc**: http://localhost:8000/api/redoc/
- **Admin Django**: http://localhost:8000/admin/
- **Esquema OpenAPI**: http://localhost:8000/api/schema/

## Estructura del Proyecto

```
OrientandoSAS API Django/
├── manage.py
├── requirements.txt
├── .env.example
├── .env (crear desde .env.example)
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    └── citas/
        ├── __init__.py
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        ├── apps.py
        ├── tests.py
        └── migrations/
```

## Modelos Principales

- **Usuario**: Gestión de usuarios del sistema
- **Cliente**: Información de clientes
- **Profesional**: Información de profesionales
- **Cita**: Gestión de citas
- **Producto**: Productos/servicios disponibles
- **EstadoChat**: Estados de conversaciones WhatsApp

## Desarrollo

### Comandos útiles

```bash
# Verificar configuración
python manage.py check

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar tests
python manage.py test

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Variables de Entorno Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_NAME` | Nombre de la base de datos | `orientando_db` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `SECRET_KEY` | Clave secreta de Django | (requerida) |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `GUNICORN_WORKERS` | Número de workers de Gunicorn | `3` |
| `PAGE_SIZE` | Elementos por página en API | `20` |

### Configuración de Gunicorn Workers

La cantidad de workers de Gunicorn se puede configurar usando la variable `GUNICORN_WORKERS`:

- **Desarrollo**: 2-3 workers
- **Producción pequeña (1-2 cores)**: 3-4 workers  
- **Producción media (4 cores)**: 5-6 workers
- **Producción grande (8+ cores)**: 8-10 workers

**Regla general**: `(CPU cores × 2) + 1`

Ver más detalles en: [GUNICORN_CONFIG.md](GUNICORN_CONFIG.md)

## Tecnologías Utilizadas

- **Django 5.2.4**: Framework web
- **Django REST Framework 3.16.0**: API REST
- **drf-spectacular 0.28.0**: Documentación automática
- **PostgreSQL**: Base de datos
- **psycopg2-binary**: Adaptador de PostgreSQL
- **python-dotenv**: Gestión de variables de entorno
