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
- `app/repositories/`: Un módulo por entidad con las constantes `_SQL_<ACCION> = """"""` vacías y documentadas para ser completadas manualmente por el equipo.
- `app/core/`: Configuración desde `.env`, pool asíncrono de PostgreSQL, excepciones de dominio (`404`, `409`, `422`, `501`) y logging.
- `sql/ddl_esquema.sql`: Esqueleto DDL en blanco con la especificación comentada de las 12 entidades en 3FN.

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
