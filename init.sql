-- Inicialización de la base de datos PostgreSQL para OrientandoSAS
-- Este script se ejecuta automáticamente al crear el contenedor de PostgreSQL

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurar zona horaria
SET timezone = 'America/Bogota';

-- Configuraciones de rendimiento
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Recargar configuración
SELECT pg_reload_conf();

-- Crear esquemas adicionales si son necesarios
-- CREATE SCHEMA IF NOT EXISTS reports;
-- CREATE SCHEMA IF NOT EXISTS logs;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos OrientandoSAS inicializada correctamente';
    RAISE NOTICE 'Zona horaria: %', current_setting('timezone');
    RAISE NOTICE 'Versión PostgreSQL: %', version();
END $$;
