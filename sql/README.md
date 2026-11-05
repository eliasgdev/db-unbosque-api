# Implementación de la base de datos (PostgreSQL)

Scripts que llevan el modelo lógico del Sistema Contable (12 entidades en 3FN) al modelo físico en PostgreSQL, y guía para instalarlo en la máquina virtual de base de datos (VM-DB).

> Los valores entre `<…>` (IPs, contraseñas) dependen de cada instalación y nunca se escriben en este repositorio.

## Contenido de la carpeta

| Script | Tipo | Qué hace | Se ejecuta como |
|---|---|---|---|
| `01_ddl_tablas.sql` | Creación de objetos | Habilita `btree_gist` y crea las 12 tablas con llaves primarias, foráneas, restricciones `UNIQUE`, `CHECK`, `EXCLUDE` y 5 índices | Dueño de la base |
| `02_seed_datos_realistas.sql` | Inserción de registros | Vacía las tablas y carga datos contables de 4 empresas dentro de una transacción | Dueño de la base |
| `03_roles_produccion.sql` | Scripts varios | Crea el usuario de la aplicación con privilegio mínimo (solo lectura y escritura de datos) | `postgres` |
| `04_algebra_relacional.sql` | Scripts varios | Las 51 sentencias de álgebra relacional del proyecto traducidas a SQL (solo consultan) | Dueño de la base |
| `05_verificacion.sql` | Scripts varios | Comprobaciones de estructura y de las reglas contables (solo consultan) | Dueño de la base |

Orden obligatorio: `01` → `02` → `03`. Los scripts `04` y `05` son opcionales y se pueden ejecutar en cualquier momento después de `02`.

## Requisitos

- PostgreSQL 13 o superior (probado con PostgreSQL 17). Desde la versión 13, `btree_gist` es una extensión de confianza: la puede habilitar el dueño de la base sin ser superusuario.
- Cliente `psql`.
- Ubuntu Server LTS en VM-DB.

## 1. Instalación en VM-DB

```bash
sudo apt update
sudo apt install -y postgresql
sudo systemctl enable --now postgresql
psql --version
```

El paquete `postgresql` de Ubuntu ya incluye las extensiones de `contrib`, entre ellas `btree_gist`.

## 2. Usuario administrador y base de datos

Se trabaja con dos usuarios distintos de `postgres`:

| Usuario | Para qué | Permisos |
|---|---|---|
| `contabilidad_admin` | Dueño de la base: crea las tablas y carga los datos | Todo sobre `contabilidad_db`, sin ser superusuario |
| `contabilidad_app` | Conexión de la API | Solo `SELECT`, `INSERT`, `UPDATE`, `DELETE` (lo crea `03`) |

```bash
sudo -u postgres psql
```

```sql
CREATE ROLE contabilidad_admin LOGIN;
\password contabilidad_admin
CREATE DATABASE contabilidad_db OWNER contabilidad_admin ENCODING 'UTF8' TEMPLATE template0;
\q
```

`\password` pide la contraseña sin mostrarla y sin dejarla en el historial de la terminal.

## 3. Ejecución de los scripts

Desde la carpeta raíz del repositorio:

```bash
# 01 y 02: como dueño de la base
psql -h localhost -U contabilidad_admin -d contabilidad_db -v ON_ERROR_STOP=1 -f sql/01_ddl_tablas.sql
psql -h localhost -U contabilidad_admin -d contabilidad_db -v ON_ERROR_STOP=1 -f sql/02_seed_datos_realistas.sql

# 03: como postgres, generando una contraseña aleatoria para la API
APP_PASSWORD="$(openssl rand -base64 24)"
sudo -u postgres psql -d contabilidad_db -v ON_ERROR_STOP=1 -v app_password="$APP_PASSWORD" -f sql/03_roles_produccion.sql
echo "$APP_PASSWORD"   # copiar en DB_PASSWORD del .env de VM-Back y cerrar la terminal
```

`-v ON_ERROR_STOP=1` detiene el script ante el primer error, para no dejar la base a medio crear. `03` debe correr como `postgres` porque crea un rol y le quita atributos de superusuario; con otro usuario falla con *permission denied to alter role*.

## 4. Conexión desde VM-Back

PostgreSQL solo debe aceptar conexiones del usuario de la aplicación y desde la IP privada de VM-Back.

1. En `/etc/postgresql/<versión>/main/postgresql.conf`:

   ```
   listen_addresses = 'localhost,<ip-privada-vm-db>'
   ```

2. Al final de `/etc/postgresql/<versión>/main/pg_hba.conf`:

   ```
   # Base       Usuario            Origen                     Método
   host contabilidad_db contabilidad_app <ip-privada-vm-back>/32 scram-sha-256
   ```

3. Firewall de la VM y reiniciar el servicio:

   ```bash
   sudo ufw allow from <ip-privada-vm-back> to any port 5432 proto tcp
   sudo systemctl restart postgresql
   ```

4. En Azure, la regla de red (NSG) de VM-DB debe permitir el puerto 5432 solo desde la IP privada de VM-Back. VM-DB no necesita IP pública.

Prueba desde VM-Back:

```bash
psql -h <ip-privada-vm-db> -U contabilidad_app -d contabilidad_db -c "SELECT current_user, count(*) FROM empresa;"
```

## 5. Verificación

Ejecutar como `contabilidad_admin`. Resultados esperados con los datos de prueba:

```sql
-- 12 tablas
SELECT count(*) AS tablas
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Restricciones por tipo: p = 12 llaves primarias, f = 17 foráneas,
-- u = 12 UNIQUE, c = 15 CHECK, x = 1 EXCLUDE
SELECT contype AS tipo, count(*)
FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace
WHERE n.nspname = 'public'
GROUP BY contype ORDER BY contype;

-- Partida doble: no debe devolver filas
SELECT id_asiento
FROM movimiento
GROUP BY id_asiento
HAVING SUM(debe) <> SUM(haber);
```

| Tabla | Registros |
|---|---|
| moneda | 6 |
| tipo_cuenta | 7 |
| tipo_asiento | 4 |
| rubro_estado | 21 |
| empresa | 4 |
| periodo_contable | 10 |
| plan_cuenta | 113 |
| tercero | 30 |
| centro_costo | 15 |
| asiento | 31 |
| movimiento | 152 |
| cierre_periodo | 6 |

También se puede ejecutar el script completo de comprobaciones, que muestra el número de tablas, las restricciones por tipo, las reglas contables (cada consulta debe devolver 0 filas) y la ecuación contable de cada empresa:

```bash
psql -h localhost -U contabilidad_admin -d contabilidad_db -f sql/05_verificacion.sql
```

## 6. Álgebra relacional en SQL

`04_algebra_relacional.sql` contiene las 51 sentencias de álgebra relacional del proyecto. Cada consulta lleva como comentario su enunciado, la expresión en álgebra y las filas que devuelve con los datos de prueba. La división (÷) se expresa con `NOT EXISTS ( … EXCEPT … )`.

```bash
psql -h localhost -U contabilidad_admin -d contabilidad_db -f sql/04_algebra_relacional.sql
```

## 7. Objetos creados por `01_ddl_tablas.sql`

| Mecanismo | Qué garantiza |
|---|---|
| Llaves primarias `BIGINT GENERATED ALWAYS AS IDENTITY` | Identificador propio en cada tabla, generado por la base |
| 17 llaves foráneas con `ON DELETE RESTRICT` | No quedan registros huérfanos ni se borra un dato que otro usa |
| Llave foránea compuesta `(id_empresa, id_cuenta_padre)` | La cuenta padre pertenece a la misma empresa |
| `UNIQUE` | NIT, código ISO, código de cuenta por empresa, número de asiento por periodo, documento de tercero por empresa, un cierre por periodo |
| `CHECK` | Estados válidos, fechas en orden, montos no negativos, cada movimiento es débito o crédito |
| `EXCLUDE USING gist` | Los periodos de una misma empresa no se traslapan |
| Índices sobre llaves foráneas | Consultas de reportes sin recorrer tablas completas |

Las reglas que comparan varias filas (la partida doble de un asiento, no registrar en periodos cerrados) se validan en la capa de servicios de la API.

## 8. Reiniciar los datos de prueba

`02_seed_datos_realistas.sql` empieza con `TRUNCATE ... RESTART IDENTITY CASCADE`, así que volver a ejecutarlo deja los datos de prueba como al inicio:

```bash
psql -h localhost -U contabilidad_admin -d contabilidad_db -v ON_ERROR_STOP=1 -f sql/02_seed_datos_realistas.sql
```

Borra todos los datos, incluidos los registrados desde la aplicación.

## 9. Respaldo y restauración

```bash
# Respaldo (formato comprimido de PostgreSQL)
pg_dump -h localhost -U contabilidad_admin -d contabilidad_db -Fc -f contabilidad_$(date +%F).dump

# Restauración en una base vacía
sudo -u postgres createdb -O contabilidad_admin -T template0 contabilidad_db
pg_restore -h localhost -U contabilidad_admin -d contabilidad_db --no-owner --no-privileges contabilidad_AAAA-MM-DD.dump
sudo -u postgres psql -d contabilidad_db -v app_password="<contraseña-de-la-api>" -f sql/03_roles_produccion.sql
```

Se restaura con `--no-privileges` y después se vuelve a ejecutar `03`, que otorga de nuevo los permisos del usuario de la aplicación.

## Problemas frecuentes

| Mensaje | Causa | Solución |
|---|---|---|
| `permission denied to create extension "btree_gist"` | PostgreSQL anterior a la versión 13, o `01` ejecutado por un usuario que no es dueño de la base | Usar PostgreSQL 13 o superior y ejecutar `01` como `contabilidad_admin` |
| `permission denied to alter role` al ejecutar `03` | `03` no se ejecutó como `postgres` | `sudo -u postgres psql ... -f sql/03_roles_produccion.sql` |
| `Connection refused` desde VM-Back | `listen_addresses`, firewall o NSG no permiten la conexión | Revisar el paso 4 |
| `no pg_hba.conf entry for host` | Falta la línea de `pg_hba.conf` o la IP no coincide | Agregarla con la IP privada exacta de VM-Back y reiniciar |
| `password authentication failed` | La contraseña del `.env` no es la del rol | Volver a ejecutar `03` con la contraseña correcta, o `ALTER ROLE contabilidad_app PASSWORD ...` como `postgres` |
| `conflicting key value violates exclusion constraint` | Se intentó crear un periodo que se cruza con otro de la misma empresa | Corregir las fechas del periodo |
