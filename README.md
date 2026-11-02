# API del Sistema Contable (Balance General y Estado de Resultados)

**Universidad El Bosque · Ingeniería de Sistemas · Bases de Datos 1 · Proyecto Final (Fase 2)**

API REST construida con **Python 3.12+**, **FastAPI**, **Pydantic v2** y **PostgreSQL (`psycopg` 3 + `psycopg_pool`)**, diseñada con SQL parametrizado puro (sin ORM) y arquitectura por capas unidireccional.

---

## Arquitectura

```text
api (routers) → services → repositories → core/database
```

- `app/api/`: Routers HTTP bajo `/api/v1`, inyección de dependencias (`deps.py`) y metadatos OpenAPI/Swagger.
- `app/schemas/`: Modelos Pydantic v2 (`Decimal` para montos monetarios, `date`/`datetime` para fechas).
- `app/services/`: Reglas contables (partida doble, periodo cerrado, cuentas hoja, cierre atómico y cálculo dinámico de Balance General y Estado de Resultados).
- `app/repositories/`: Un módulo por entidad con las constantes `_SQL_<ACCION>` documentadas (propósito, parámetros, retorno y tablas) y escritas manualmente por el equipo con SQL parametrizado.
- `app/core/`: Configuración desde `.env`, pool asíncrono de PostgreSQL, excepciones de dominio (`404`, `409`, `422`, `501`) y logging.
- `sql/01_ddl_tablas.sql`: DDL de PostgreSQL con las 12 entidades en 3FN, sus restricciones e índices.
- `sql/02_seed_datos_realistas.sql`: Datos de prueba realistas (4 empresas, 10 periodos, plan de cuentas, asientos y cierres).

---

## Configuración (`.env`)

Toda la configuración proviene exclusivamente del archivo `.env`. Cree su archivo local a partir de la plantilla:

```bash
cp .env.example .env
```

Si falta cualquier variable obligatoria en `.env`, la aplicación fallará al iniciar indicando exactamente qué variables faltan.

---

## Instalación y Ejecución (`uv` y `pip`)

### Opción A: Usando `uv`

```bash
uv sync
uv run uvicorn app.main:app --reload
```

### Opción B: Usando `pip`

```bash
python -m venv .venv
# En Linux/macOS:
source .venv/bin/activate
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

---

## Documentación Interactiva

Una vez iniciado el servidor:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Esquema OpenAPI**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/api/v1/health` (y `http://localhost:8000/health`)

---

## Verificación de Calidad

Antes de cada Pull Request, ejecute las validaciones de estilo, formato y tipado estático:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app
```

---

## Despliegue en producción (VM-Back)

La API corre en VM-Back detrás del nginx de VM-Front; no se expone a internet. `/docs` y `/redoc` quedan accesibles solo desde la red privada, porque nginx únicamente reenvía `/api/`.

### 1. Base de datos (VM-DB)

```bash
psql -d contabilidad_db -f sql/01_ddl_tablas.sql
psql -d contabilidad_db -f sql/02_seed_datos_realistas.sql
psql -d contabilidad_db -v app_password="$(openssl rand -base64 24)" -f sql/03_roles_produccion.sql
```

`03_roles_produccion.sql` crea `contabilidad_app`, que solo puede leer y escribir datos (no crear, alterar ni borrar tablas). Guarde la contraseña generada para el `.env`. En `pg_hba.conf`, permita a ese usuario conectarse únicamente desde la IP privada de VM-Back.

### 2. Código y entorno (VM-Back)

```bash
sudo useradd --system --home /opt/db-unbosque-api --shell /usr/sbin/nologin contable
sudo git clone https://github.com/eliasgdev/db-unbosque-api.git /opt/db-unbosque-api
cd /opt/db-unbosque-api
sudo python3 -m venv .venv && sudo .venv/bin/pip install -r requirements.txt
sudo cp .env.example .env    # completar con los valores reales
sudo chown -R contable:contable /opt/db-unbosque-api
sudo chmod 600 .env
```

Valores de `.env` para producción:

| Variable | Valor |
|---|---|
| `APP_ENV` | `production` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | `http://<dominio-del-front>` (el front y la API comparten dominio a través del proxy) |
| `FORWARDED_ALLOW_IPS` | IP privada de VM-Front, la única autorizada a enviar cabeceras de proxy |
| `DB_HOST` | IP privada de VM-DB |
| `DB_USER` / `DB_PASSWORD` | `contabilidad_app` y la contraseña generada en el paso 1 |
| `DB_SSLMODE` | `require` si PostgreSQL tiene SSL habilitado; si no, `prefer` |

### 3. Servicio systemd

```bash
sudo cp deploy/contable-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now contable-api
systemctl status contable-api
curl http://localhost:8000/api/v1/health
```

El servicio corre como el usuario `contable` (sin privilegios), se reinicia solo si falla y confía en las cabeceras de proxy únicamente desde el nginx de VM-Front (`--forwarded-allow-ips`).

### 4. Red

- VM-Back acepta el puerto 8000 solo desde la IP privada de VM-Front.
- VM-DB acepta el puerto 5432 solo desde la IP privada de VM-Back.
- Ninguna de las dos necesita IP pública; se administran por SSH a través de VM-Front o de Azure Bastion.

### Actualizar a una nueva versión

```bash
cd /opt/db-unbosque-api
sudo -u contable git pull
sudo -u contable .venv/bin/pip install -r requirements.txt
sudo systemctl restart contable-api
```
