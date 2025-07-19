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

# Copiar y hacer ejecutables los scripts
COPY wait-for-postgres.sh /app/wait-for-postgres.sh
COPY start.sh /app/start.sh
RUN chmod +x /app/wait-for-postgres.sh /app/start.sh

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["./start.sh"]
