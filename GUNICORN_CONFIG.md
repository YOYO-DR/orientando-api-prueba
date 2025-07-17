# Configuración de Gunicorn Workers

## Variable de Entorno GUNICORN_WORKERS

Ahora puedes configurar el número de workers de Gunicorn usando la variable de entorno `GUNICORN_WORKERS`.

### Configuración

#### Por defecto
Si no se especifica la variable, Gunicorn usará **3 workers** (valor por defecto).

#### Configurar workers personalizados

##### En Docker Compose (desarrollo local)
```bash
# En tu archivo .env o al ejecutar docker-compose
GUNICORN_WORKERS=4 docker-compose -f docker-compose.simple.yml up
```

##### En Dokploy (producción)
1. Ve a tu aplicación en Dokploy
2. En la sección "Environment Variables"
3. Añade la variable:
   - **Nombre**: `GUNICORN_WORKERS`
   - **Valor**: `4` (o el número que desees)

##### En Docker Compose de producción
```bash
# Al ejecutar el contenedor
GUNICORN_WORKERS=5 docker-compose -f docker-compose.prod.yml up
```

### Recomendaciones para el número de workers

#### Regla general
- **CPU cores × 2 + 1**
- Ejemplo: Si tienes 2 cores → (2 × 2) + 1 = 5 workers

#### Por tipo de servidor
- **Servidor pequeño (1 core)**: 2-3 workers
- **Servidor medio (2 cores)**: 4-5 workers  
- **Servidor grande (4+ cores)**: 8-10 workers

#### Consideraciones
- **Más workers NO siempre es mejor**
- Demasiados workers pueden consumir mucha memoria
- Monitorea el uso de RAM y CPU antes de aumentar

### Archivos modificados

Los siguientes archivos ahora soportan la variable `GUNICORN_WORKERS`:

1. `docker-compose.dokploy.yml` - Para deployment en Dokploy
2. `docker-compose.prod.yml` - Para producción con PostgreSQL incluido
3. `docker-compose.simple.yml` - Para desarrollo y testing

### Ejemplo de uso

```bash
# Desarrollo con 2 workers
GUNICORN_WORKERS=2 docker-compose -f docker-compose.simple.yml up

# Producción con 6 workers
GUNICORN_WORKERS=6 docker-compose -f docker-compose.prod.yml up -d

# En Dokploy: configurar GUNICORN_WORKERS=4 en las variables de entorno
```

### Verificar configuración

Puedes verificar que Gunicorn está usando el número correcto de workers revisando los logs del contenedor:

```bash
docker logs orientando_web
```

Deberías ver algo como:
```
[INFO] Starting gunicorn with 4 workers
[INFO] Listening at: http://0.0.0.0:8000
```
