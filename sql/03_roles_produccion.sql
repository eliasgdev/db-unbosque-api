-- ============================================================================
-- 03_ROLES_PRODUCCION.SQL — USUARIO DE LA APLICACIÓN CON PRIVILEGIO MÍNIMO
-- ============================================================================
-- La API no debe conectarse como superusuario ni como dueño de las tablas.
-- Este script crea el rol contabilidad_app con permisos solo de lectura y
-- escritura de datos (DML): no puede crear, alterar ni borrar tablas.
--
-- Ejecutar como administrador DESPUÉS de 01 y 02, pasando la contraseña como
-- variable (no queda escrita en el script ni en el historial de Git):
--   psql -d contabilidad_db -v app_password="$(openssl rand -base64 24)" \
--        -f sql/03_roles_produccion.sql
-- Copiar esa misma contraseña en DB_PASSWORD del .env de VM-Back.
-- ============================================================================

SELECT format('CREATE ROLE contabilidad_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'contabilidad_app')
\gexec

ALTER ROLE contabilidad_app NOSUPERUSER NOCREATEDB NOCREATEROLE;

GRANT CONNECT ON DATABASE contabilidad_db TO contabilidad_app;
GRANT USAGE ON SCHEMA public TO contabilidad_app;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO contabilidad_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO contabilidad_app;

-- Tablas que se creen después también quedan con los mismos permisos.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO contabilidad_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO contabilidad_app;
