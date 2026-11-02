# User Brief — API del Sistema Contable (Balance General y Estado de Resultados)

Universidad El Bosque · Ingeniería de Sistemas · Bases de Datos 1 · Proyecto Final (Fase 2)

| Campo | Valor |
|---|---|
| Componente | Backend (API REST) |
| Stack | Python 3.12+ · FastAPI · PostgreSQL · SQL puro |
| Despliegue | VM en la nube (VM-Back, Ubuntu Server 26.04 LTS) |
| Fuentes | Propuesta de proyecto, Documento de supuestos (S-01…S-37), Análisis de selección de SO |

---

## 1. Problema

Las pymes llevan la contabilidad en hojas de cálculo desconectadas. Consecuencias:

- Saldos digitados a mano → errores y duplicidad.
- Sin control de **partida doble** por asiento.
- Sin plan de cuentas uniforme → el balance se reconstruye a mano cada periodo.
- Sin trazabilidad de qué asiento originó cada saldo ni bloqueo de periodos cerrados.
- El Balance no cuadra al cierre: la utilidad del ejercicio no llega al patrimonio.

Causa raíz: **no existe un modelo de datos normalizado y consistente** que centralice plan de cuentas, asientos y periodos.

## 2. Solución

API REST que expone el modelo contable (12 entidades, 3FN) y:

1. Registra empresas, periodos, plan de cuentas jerárquico, terceros, centros de costo y asientos con movimientos débito/crédito.
2. Aplica las reglas contables en la capa de servicios (partida doble, periodo cerrado, cuentas hoja).
3. Cierra periodos y traslada la utilidad/pérdida al patrimonio.
4. Calcula, sin almacenarlos, el **Balance General** y el **Estado de Resultados** a partir de los movimientos contabilizados (S-07).
5. Se documenta con Swagger/OpenAPI y es consumida por la aplicación web de demostración.

## 3. Alcance

### 3.1 Incluye

| Módulo | Capacidad | RF |
|---|---|---|
| Empresas y monedas | Alta y consulta de empresa (NIT, razón social, moneda base); catálogo de monedas | RF-01 |
| Periodos | Crear/consultar periodos (inicio, fin, estado); sin traslape; abierto/cerrado | RF-02 |
| Plan de cuentas | Jerarquía recursiva por empresa, tipo de cuenta, rubro de estado, marca `acepta_movimiento` | RF-03, 04, 05 |
| Asientos | Registro con N movimientos, tipo (apertura, diario, ajuste, cierre), periodo, estado borrador/contabilizado | RF-06, 07, 08 |
| Terceros y centros de costo | CRUD básico y asociación opcional a movimientos | RF-10 |
| Cierre de periodo | Calcula utilidad, genera asiento de cierre, marca periodo cerrado | RF-11, 12 |
| Estado de Resultados | Ingresos, costos, gastos, utilidad bruta, operacional y neta por periodo | RF-13 |
| Balance General | Agrupado por rubros a fecha de corte; verifica Activo = Pasivo + Patrimonio | RF-14 |
| Consulta para la web | Plan de cuentas, asientos de un periodo y ambos reportes | RF-09, RF-15 |
| Documentación | Swagger UI (`/docs`) y ReDoc (`/redoc`) | — |
| Operación | Endpoint `/health` | — |

### 3.2 No incluye

- Facturación electrónica, nómina, inventarios, integración tributaria.
- Estado de Flujo de Efectivo y Estado de Cambios en el Patrimonio (S-30).
- Autenticación, roles y auditoría detallada (S-29).
- Conversión de moneda o diferencias en cambio (S-19).
- Almacenamiento de saldos o reportes (S-07).
- **Pruebas de cualquier tipo** (unitarias, integración, e2e, carga).
- ORM, migraciones automáticas y generación de esquema desde código.
- Frontend, scripts de carga de datos de prueba y aprovisionamiento de la VM (documentos aparte).

## 4. Stack y herramientas

| Aspecto | Decisión |
|---|---|
| Lenguaje | Python 3.12+ |
| Framework | FastAPI + Uvicorn |
| Validación y config | Pydantic v2 + `pydantic-settings` (lectura de `.env`) |
| Base de datos | PostgreSQL (RDBMS distinto de SQL Server) |
| Driver | `psycopg` 3 + `psycopg_pool` (pool asíncrono), **SQL parametrizado, sin ORM** |
| Gestor de dependencias | `uv`, **compatible con `pip`** |
| Calidad | `ruff` (lint + formato) y `mypy` |
| Documentación API | OpenAPI automático de FastAPI |
| Control de versiones | Git + GitHub |

## 5. Gestión de dependencias (uv + pip)

El equipo mezcla `uv` y `pip`; ambos deben funcionar sin pasos extra.

| Archivo | Rol | Versionado |
|---|---|---|
| `pyproject.toml` | Fuente de verdad (PEP 621): dependencias, dev-group, config de `ruff` y `mypy` | Sí |
| `uv.lock` | Lock reproducible para quien use `uv` | Sí |
| `requirements.txt` | Exportado del lock, para `pip` y la VM | Sí |
| `requirements-dev.txt` | Exportado con herramientas de calidad | Sí |

Flujo:

```bash
# uv
uv sync
uv run uvicorn app.main:app --reload

# pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# al agregar una dependencia (quien use uv)
uv add <paquete>
uv export --no-hashes --no-dev -o requirements.txt
uv export --no-hashes --only-dev -o requirements-dev.txt   # o --all-groups
```

Regla: todo cambio de dependencias se commitea junto con `uv.lock` y los `requirements*.txt` regenerados. Quien use `pip` no edita `requirements*.txt` a mano.

## 6. Configuración

- **Única fuente de configuración: el archivo `.env`.** Sin valores hardcodeados, sin archivos de config alternos, sin defaults de secretos en código.
- `.env` **no se versiona**; `.env.example` sí, con todas las variables y valores ficticios.
- Se lee una sola vez en `app/core/config.py` (clase `Settings`, cacheada) y se inyecta donde se necesite.
- En la VM se carga con `EnvironmentFile=` de systemd o equivalente; el código no cambia entre entornos.

| Variable | Propósito |
|---|---|
| `APP_NAME` | Título mostrado en Swagger |
| `APP_ENV` | `development` / `production` |
| `APP_HOST`, `APP_PORT` | Interfaz y puerto de Uvicorn |
| `LOG_LEVEL` | Nivel de logging |
| `CORS_ORIGINS` | Orígenes permitidos (la web de demostración), separados por coma |
| `DB_HOST`, `DB_PORT`, `DB_NAME` | Ubicación de PostgreSQL (VM-DB) |
| `DB_USER`, `DB_PASSWORD` | Credenciales |
| `DB_SSLMODE` | Modo SSL de conexión |
| `DB_POOL_MIN`, `DB_POOL_MAX` | Tamaño del pool |

## 7. Arquitectura

Paquete raíz `app/`, arquitectura por capas con dependencia **unidireccional**:

`api (routers) → services → repositories → core/database`

| Capa | Responsabilidad | Prohibido |
|---|---|---|
| `app/api/` | Routers, dependencias, mapeo de excepciones a HTTP, metadatos Swagger | Lógica de negocio, SQL |
| `app/schemas/` | Modelos Pydantic de entrada/salida (DTOs) | Acceso a datos |
| `app/services/` | Reglas de negocio y orquestación de transacciones | SQL, objetos HTTP |
| `app/repositories/` | Un módulo por entidad; ejecuta SQL parametrizado y devuelve dicts/DTOs | Reglas de negocio |
| `app/core/` | Config, pool de conexiones, excepciones de dominio, logging | Lógica de dominio |

```text
.
├── app/
│   ├── main.py                    # create_app(), routers, handlers, lifespan (pool)
│   ├── api/
│   │   ├── deps.py                # inyección de servicios y conexión
│   │   └── v1/
│   │       ├── router.py          # agrega routers bajo /api/v1
│   │       ├── empresas.py
│   │       ├── monedas.py
│   │       ├── periodos.py
│   │       ├── cuentas.py
│   │       ├── catalogos.py       # tipos de cuenta, rubros, tipos de asiento
│   │       ├── asientos.py
│   │       ├── terceros.py
│   │       ├── centros_costo.py
│   │       ├── reportes.py        # balance general y estado de resultados
│   │       └── health.py
│   ├── core/
│   │   ├── config.py              # Settings desde .env
│   │   ├── database.py            # pool, transacción, ejecución de SQL
│   │   ├── exceptions.py          # excepciones de dominio
│   │   └── logging.py
│   ├── schemas/                   # un módulo por entidad
│   ├── services/                  # un módulo por agregado
│   └── repositories/              # un módulo por entidad
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

Reglas transversales:

- Transacciones abiertas en la capa de servicios; los repositorios reciben la conexión.
- Excepciones de dominio (`NoEncontrado`, `ReglaDeNegocio`, `Conflicto`, `SqlNoDefinido`) definidas en `core/` y traducidas a 404/422/409/501 en `api/`.
- Sin `print`; solo `logging`. Sin variables globales mutables.
- Prohibido concatenar o formatear strings en SQL: **solo parámetros** (`%s` / nombrados) para evitar inyección.

## 8. Restricciones de implementación

| # | Restricción |
|---|---|
| 1 | **Sin ORM** (SQLAlchemy, Tortoise, SQLModel, Django ORM, etc.). SQL puro. |
| 2 | **Sin testing de ningún tipo**: no `pytest`, no carpeta `tests/`, no mocks, no cobertura. |
| 3 | **Sentencias SQL vacías** (sección 9). |
| 4 | Configuración solo por `.env`. |
| 5 | Compatible con `pip` y `uv`. |
| 6 | Arquitectura por capas bajo `app/`; los routers no tocan la base de datos. |
| 7 | Saldos y totales calculados, nunca persistidos. |
| 8 | Solo asientos `CONTABILIZADO` entran a los reportes (RF-09). |
| 9 | Ejecutable en una VM Linux; sin dependencias de SO propietarias. |

## 9. Sentencias SQL: se dejan vacías

Todas las sentencias SQL (consultas, inserciones, actualizaciones, creación de objetos) **se entregan vacías**; el equipo las escribe y modifica **manualmente**. El código solo debe proveer el esqueleto y documentar su propósito.

Convención en cada repositorio:

```python
# Propósito: obtener una empresa por su identificador.
# Parámetros: id_empresa (int).
# Retorna: una fila de EMPRESA o ninguna.
# Tablas: EMPRESA, MONEDA.
_SQL_OBTENER_POR_ID = """"""
```

Reglas:

- Una constante `_SQL_<ACCION>` por sentencia, con comentario inmediatamente encima que indique **propósito, parámetros, retorno y tablas involucradas**.
- Contenido en blanco: no incluir `SELECT`, `INSERT`, esbozos ni "TODO" con SQL.
- `core/database.py` lanza `SqlNoDefinido` (HTTP 501) si se ejecuta una sentencia vacía; así el API arranca y Swagger se documenta aunque el SQL no esté listo.
- Las sentencias de creación del esquema (DDL) siguen la misma convención: archivos en blanco con el propósito de cada objeto como comentario. No se generan migraciones automáticas.
- La inferencia de tipos de la sección 11 sirve para documentar y para los esquemas Pydantic, no para escribir DDL.

## 10. Convenciones de Python y calidad

| Tema | Estándar |
|---|---|
| Estilo | PEP 8; formato y lint con `ruff` (línea ≤ 88) |
| Tipado | PEP 484: anotaciones en todas las firmas; `mypy` sin errores |
| Docstrings | PEP 257 en módulos, clases y funciones públicas |
| Nombres | `snake_case` (funciones, variables, módulos), `PascalCase` (clases), `UPPER_SNAKE_CASE` (constantes) |
| Idioma | Dominio en español (`asiento`, `periodo`), consistente con el modelo de datos; identificadores sin tildes ni ñ |
| Imports | Absolutos desde `app.`, ordenados por `ruff` (isort) |
| Funciones | Una responsabilidad; sin lógica en `main.py` salvo ensamblado |
| Errores | Excepciones de dominio; nunca `except:` desnudo |
| Dinero | `decimal.Decimal`, nunca `float` |
| Fechas | `datetime.date` / `datetime.datetime` con zona horaria donde aplique |
| Commits | Pequeños, con mensaje descriptivo; contribución de todos visible en GitHub |

Verificación previa a cada PR (manual, sin tests):

```bash
ruff check .
ruff format --check .
mypy app
```

## 11. Modelo de datos

12 entidades, 3FN, tipos PostgreSQL. Llaves primarias `BIGINT GENERATED ALWAYS AS IDENTITY`. Los atributos **no marcados con †** salen de los documentos; los marcados con † son **inferidos** y deben confirmarse.

### 11.1 Tablas

| Tabla | Columna | Tipo | Restricciones |
|---|---|---|---|
| **MONEDA** | id_moneda | BIGINT | PK |
| | codigo | VARCHAR(3) | UNIQUE, NOT NULL (ej. COP) |
| | nombre | VARCHAR(60) | NOT NULL |
| | simbolo | VARCHAR(5) | NOT NULL |
| **EMPRESA** | id_empresa | BIGINT | PK |
| | nit | VARCHAR(20) | UNIQUE, NOT NULL |
| | razon_social | VARCHAR(200) | NOT NULL |
| | id_moneda | BIGINT | FK → MONEDA, NOT NULL |
| **PERIODO_CONTABLE** | id_periodo | BIGINT | PK |
| | id_empresa | BIGINT | FK → EMPRESA, NOT NULL |
| | fecha_inicio | DATE | NOT NULL |
| | fecha_fin | DATE | NOT NULL, CHECK (fecha_fin > fecha_inicio) |
| | estado | VARCHAR(10) | CHECK IN ('ABIERTO','CERRADO'), NOT NULL |
| **TIPO_CUENTA** | id_tipo_cuenta | BIGINT | PK |
| | clase | VARCHAR(15) | UNIQUE, CHECK IN ('ACTIVO','PASIVO','PATRIMONIO','INGRESO','COSTO','GASTO') |
| | naturaleza | VARCHAR(7) | CHECK IN ('DEBITO','CREDITO'), NOT NULL |
| **RUBRO_ESTADO** | id_rubro | BIGINT | PK |
| | id_rubro_padre | BIGINT | FK → RUBRO_ESTADO, NULL (recursiva) |
| | codigo † | VARCHAR(20) | UNIQUE, NOT NULL |
| | nombre | VARCHAR(150) | NOT NULL |
| | estado_financiero | VARCHAR(10) | CHECK IN ('BALANCE','RESULTADOS'), NOT NULL |
| | orden † | SMALLINT | NOT NULL (orden de presentación) |
| **PLAN_CUENTA** | id_cuenta | BIGINT | PK |
| | id_empresa | BIGINT | FK → EMPRESA, NOT NULL |
| | id_cuenta_padre | BIGINT | FK → PLAN_CUENTA, NULL (recursiva) |
| | id_tipo_cuenta | BIGINT | FK → TIPO_CUENTA, NOT NULL |
| | id_rubro | BIGINT | FK → RUBRO_ESTADO, NOT NULL |
| | codigo † | VARCHAR(20) | NOT NULL, UNIQUE (id_empresa, codigo) |
| | nombre | VARCHAR(150) | NOT NULL |
| | nivel † | SMALLINT | NOT NULL (clase, grupo, cuenta, subcuenta) |
| | acepta_movimiento | BOOLEAN | NOT NULL |
| **TIPO_ASIENTO** | id_tipo_asiento | BIGINT | PK |
| | nombre | VARCHAR(10) | UNIQUE, CHECK IN ('APERTURA','DIARIO','AJUSTE','CIERRE') |
| **ASIENTO** | id_asiento | BIGINT | PK |
| | id_periodo | BIGINT | FK → PERIODO_CONTABLE, NOT NULL |
| | id_tipo_asiento | BIGINT | FK → TIPO_ASIENTO, NOT NULL |
| | numero † | INTEGER | NOT NULL, UNIQUE (id_periodo, numero) |
| | fecha | DATE | NOT NULL (dentro del rango del periodo) |
| | descripcion † | VARCHAR(300) | NOT NULL |
| | estado | VARCHAR(13) | CHECK IN ('BORRADOR','CONTABILIZADO'), NOT NULL |
| **TERCERO** | id_tercero | BIGINT | PK |
| | id_empresa | BIGINT | FK → EMPRESA, NOT NULL |
| | documento | VARCHAR(20) | NOT NULL, UNIQUE (id_empresa, documento) |
| | nombre † | VARCHAR(200) | NOT NULL |
| | tipo † | VARCHAR(10) | CHECK IN ('CLIENTE','PROVEEDOR','OTRO') |
| **CENTRO_COSTO** | id_centro_costo | BIGINT | PK |
| | id_empresa | BIGINT | FK → EMPRESA, NOT NULL |
| | codigo † | VARCHAR(20) | NOT NULL, UNIQUE (id_empresa, codigo) |
| | nombre † | VARCHAR(150) | NOT NULL |
| **MOVIMIENTO** | id_movimiento | BIGINT | PK |
| | id_asiento | BIGINT | FK → ASIENTO, NOT NULL |
| | id_cuenta | BIGINT | FK → PLAN_CUENTA, NOT NULL |
| | id_tercero | BIGINT | FK → TERCERO, NULL |
| | id_centro_costo | BIGINT | FK → CENTRO_COSTO, NULL |
| | debe | NUMERIC(20,2) | NOT NULL, DEFAULT 0, CHECK (debe >= 0) |
| | haber | NUMERIC(20,2) | NOT NULL, DEFAULT 0, CHECK (haber >= 0) |
| | | | CHECK: solo uno de `debe`/`haber` distinto de cero (S-21) |
| **CIERRE_PERIODO** | id_cierre | BIGINT | PK |
| | id_periodo | BIGINT | FK → PERIODO_CONTABLE, UNIQUE, NOT NULL (1:1) |
| | id_asiento_cierre † | BIGINT | FK → ASIENTO, UNIQUE, NULL |
| | utilidad_neta | NUMERIC(20,2) | NOT NULL |
| | fecha_cierre † | TIMESTAMPTZ | NOT NULL |

### 11.2 Relaciones

| Tipo | Relación |
|---|---|
| 1:1 | PERIODO_CONTABLE — CIERRE_PERIODO |
| 1:N | MONEDA→EMPRESA · EMPRESA→PERIODO_CONTABLE, PLAN_CUENTA, TERCERO, CENTRO_COSTO · TIPO_CUENTA→PLAN_CUENTA · RUBRO_ESTADO→PLAN_CUENTA · TIPO_ASIENTO→ASIENTO · PERIODO_CONTABLE→ASIENTO · ASIENTO→MOVIMIENTO · TERCERO→MOVIMIENTO · CENTRO_COSTO→MOVIMIENTO |
| M:N | ASIENTO ↔ PLAN_CUENTA, resuelta con MOVIMIENTO |
| Recursivas | PLAN_CUENTA (padre/hijas) · RUBRO_ESTADO (padre/subrubros) |

Un asiento llega a la empresa solo a través de su periodo (S-18).

## 12. Reglas de negocio (capa `services`)

| Regla | Dónde se valida | RF / S |
|---|---|---|
| Σ debe = Σ haber al contabilizar un asiento | Servicio de asientos | RF-07, S-01 |
| Movimientos solo sobre cuentas con `acepta_movimiento = true` | Servicio de asientos | RF-05, S-05 |
| Fecha del asiento dentro del rango de su periodo | Servicio de asientos | S-14 |
| No crear ni modificar asientos en periodo `CERRADO` | Servicio de asientos | RF-12, S-15 |
| Periodos de una empresa no se traslapan | Servicio de periodos | S-13 |
| Tercero y centro de costo opcionales en movimiento | Esquema Pydantic + servicio | RF-10, S-23 |
| Cuenta, tercero y centro de costo pertenecen a la misma empresa que el periodo | Servicio de asientos | S-06, S-18 |
| Cierre: calcula utilidad, genera asiento `CIERRE`, marca periodo `CERRADO`, una sola vez por periodo | Servicio de periodos (una transacción) | RF-11, S-16, S-17 |
| Reportes consideran solo asientos `CONTABILIZADO` | Repositorio de reportes | RF-09, S-08 |
| Estado de Resultados = Ingresos − Costos − Gastos; muestra utilidad bruta, operacional y neta según rubros | Servicio de reportes | RF-13, S-10 |
| Balance incluye la utilidad del ejercicio y devuelve indicador `cuadra` (Activo = Pasivo + Patrimonio) | Servicio de reportes | RF-14, S-09 |
| Estructura de los reportes definida por `RUBRO_ESTADO`, no por código | Servicio de reportes | S-11 |

Las mismas reglas deben reforzarse con restricciones `CHECK`/`UNIQUE`/`EXCLUDE` creadas manualmente en la base de datos.

## 13. Endpoints

Prefijo `/api/v1`. Todos con `tags`, `summary`, `description`, `response_model` y códigos de error documentados.

| Método | Ruta | Descripción | RF |
|---|---|---|---|
| GET | `/health` | Estado del servicio y conexión a BD | — |
| GET | `/monedas` | Catálogo de monedas | RF-01 |
| POST | `/empresas` | Registrar empresa | RF-01 |
| GET | `/empresas` · `/empresas/{id_empresa}` | Listar / consultar empresa | RF-01 |
| POST | `/empresas/{id_empresa}/periodos` | Crear periodo contable | RF-02 |
| GET | `/empresas/{id_empresa}/periodos` · `/periodos/{id_periodo}` | Listar / consultar periodos | RF-02, 15 |
| POST | `/periodos/{id_periodo}/cierre` | Cerrar periodo y generar asiento de cierre | RF-11 |
| GET | `/periodos/{id_periodo}/cierre` | Consultar cierre y utilidad trasladada | RF-11 |
| GET | `/tipos-cuenta` · `/rubros-estado` · `/tipos-asiento` | Catálogos de solo lectura | RF-04, 08 |
| POST | `/empresas/{id_empresa}/cuentas` | Crear cuenta del plan | RF-03, 04, 05 |
| GET | `/empresas/{id_empresa}/cuentas` · `/cuentas/{id_cuenta}` | Plan de cuentas (jerárquico) / cuenta | RF-03, 15 |
| POST | `/empresas/{id_empresa}/terceros` · GET (listar) | Terceros | RF-10 |
| POST | `/empresas/{id_empresa}/centros-costo` · GET (listar) | Centros de costo | RF-10 |
| POST | `/periodos/{id_periodo}/asientos` | Registrar asiento con movimientos (borrador) | RF-06, 08, 12 |
| GET | `/periodos/{id_periodo}/asientos` · `/asientos/{id_asiento}` | Asientos de un periodo / detalle con movimientos | RF-15 |
| PUT | `/asientos/{id_asiento}` | Modificar asiento en borrador de periodo abierto | RF-12 |
| POST | `/asientos/{id_asiento}/contabilizar` | Validar partida doble y contabilizar | RF-07, 09 |
| GET | `/periodos/{id_periodo}/estado-resultados` | Estado de Resultados | RF-13 |
| GET | `/empresas/{id_empresa}/balance-general?fecha_corte=YYYY-MM-DD` | Balance General a fecha de corte | RF-14 |

Códigos de error estándar: `404` no encontrado · `409` conflicto (traslape, duplicado, ya cerrado) · `422` validación o regla de negocio · `501` SQL no definido · `500` inesperado.

## 14. Documentación Swagger

- `/docs` (Swagger UI) y `/redoc` habilitados; `openapi.json` accesible.
- Metadatos de la app: título (`APP_NAME`), versión, descripción del proyecto, `openapi_tags` con descripción por módulo.
- Cada endpoint: `summary`, `description`, `response_model`, `responses` para 404/409/422 y `status_code` explícito.
- Cada campo Pydantic con `Field(description=..., examples=[...])`.
- Ejemplos de request/response en los esquemas de asiento, Balance General y Estado de Resultados.
- La documentación debe ser completa aunque el SQL esté vacío.

## 15. Despliegue

| Aspecto | Decisión |
|---|---|
| Servidor | VM-Back, Ubuntu Server 26.04 LTS (Azure) |
| Proceso | Uvicorn gestionado por `systemd`, con `EnvironmentFile` apuntando al `.env` |
| Entrada | Proxy inverso en VM-Front; la API no se expone directamente |
| Base de datos | PostgreSQL en VM-DB, accesible solo desde VM-Back |
| Instalación | `pip install -r requirements.txt` en un entorno virtual |
| Secretos | Solo en `.env` de la VM, permisos `600`, fuera de Git |
| Versión de SO | Verificar disponibilidad de imagen 26.04 y de paquetes de PostgreSQL antes del despliegue (plan alterno: 24.04 LTS) |

## 16. Criterios de aceptación

- [ ] La API arranca solo con un `.env` válido y falla con mensaje claro si falta una variable.
- [ ] `uv sync` y `pip install -r requirements.txt` producen un entorno funcional.
- [ ] Ningún módulo importa un ORM; ninguna sentencia SQL tiene contenido, y cada una tiene su comentario de propósito.
- [ ] Estructura `app/api`, `app/core`, `app/repositories`, `app/schemas`, `app/services` respetada; sin SQL fuera de `repositories`.
- [ ] Los 15 RF tienen endpoint y regla asignada (secciones 12 y 13).
- [ ] Swagger documenta todos los endpoints, esquemas y errores.
- [ ] `ruff check`, `ruff format --check` y `mypy app` sin errores.
- [ ] No existe código ni dependencias de testing.

## 17. Pendientes por confirmar

| # | Tema | Supuesto adoptado |
|---|---|---|
| 1 | Atributos por tabla | Inferidos de los documentos; los marcados con † son propuestos. Reemplazar por los atributos definitivos del equipo. |
| 2 | S-28 (web de solo lectura) vs. RF-01…RF-12 (registro) | La API implementa registro y consulta para cubrir los RF; la web de demostración solo consume `GET`. |
| 3 | "SQL vacías" | Se interpreta como todas las sentencias (DML y DDL) vacías con comentario de propósito. |
| 4 | Driver y modo | `psycopg` 3 asíncrono con pool; cambiable a síncrono sin afectar la arquitectura. |
| 5 | Moneda y tercero como entidad por empresa | `TERCERO` y `CENTRO_COSTO` pertenecen a una empresa (1:N desde EMPRESA, según propuesta). |