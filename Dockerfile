# Usar Python 3.12 como imagen base
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
        curl \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Crear directorios necesarios
RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/media
RUN mkdir -p /app/logs

# Crear script para esperar a que PostgreSQL esté listo
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
host="$1"\n\
port="$2"\n\
shift 2\n\
cmd="$@"\n\
\n\
until nc -z "$host" "$port"; do\n\
  >&2 echo "PostgreSQL is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
\n\
>&2 echo "PostgreSQL is up - executing command"\n\
exec $cmd' > /app/wait-for-postgres.sh

# Hacer ejecutable el script
RUN chmod +x /app/wait-for-postgres.sh

# Crear script de inicio
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Esperar a que PostgreSQL esté disponible\n\
./wait-for-postgres.sh db 5432\n\
\n\
# Crear directorios si no existen\n\
echo "Creando directorios necesarios..."\n\
mkdir -p /app/staticfiles\n\
mkdir -p /app/media\n\
mkdir -p /app/logs\n\
\n\
# Ejecutar migraciones\n\
echo "Aplicando migraciones..."\n\
python manage.py migrate --noinput\n\
\n\
# Recopilar archivos estáticos\n\
echo "Recopilando archivos estáticos..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
# Crear superusuario si no existe\n\
echo "Verificando superusuario..."\n\
python manage.py shell -c "\n\
from django.contrib.auth.models import User;\n\
if not User.objects.filter(username='\''admin'\'').exists():\n\
    User.objects.create_superuser('\''admin'\'', '\''admin@orientando.com'\'', '\''admin123'\'')\n\
    print('\''Superusuario creado: admin/admin123'\'')\n\
else:\n\
    print('\''Superusuario ya existe'\'')\n\
"\n\
\n\
# Iniciar servidor\n\
echo "Iniciando servidor Django..."\n\
python manage.py runserver 0.0.0.0:8000' > /app/start.sh

# Hacer ejecutable el script de inicio
RUN chmod +x /app/start.sh

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["./start.sh"]
