"""Punto de entrada y ensamblado de la API del Sistema Contable.

Inicializa la aplicación FastAPI, el ciclo de vida del pool de conexiones a
PostgreSQL, el middleware CORS, los manejadores globales de excepciones de
dominio y la documentación OpenAPI/Swagger.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import health
from app.api.v1.router import api_v1_router
from app.core.config import obtener_settings
from app.core.database import GestorBaseDatos
from app.core.exceptions import (
    Conflicto,
    NoEncontrado,
    ReglaDeNegocio,
    SqlNoDefinido,
)
from app.core.logging import configurar_logging, obtener_logger
from app.schemas.comun import ErrorResponse

logger = obtener_logger(__name__)

OPENAPI_TAGS: list[dict[str, Any]] = [
    {
        "name": "Operación",
        "description": (
            "Verificación del estado del servicio y conectividad con PostgreSQL."
        ),
    },
    {
        "name": "Monedas",
        "description": "Catálogo de monedas funcionales para las empresas (RF-01).",
    },
    {
        "name": "Empresas",
        "description": "Alta y consulta de empresas con su NIT y moneda base (RF-01).",
    },
    {
        "name": "Periodos",
        "description": (
            "Apertura, consulta y cierre atómico de periodos contables con "
            "traslado de utilidad al patrimonio (RF-02, RF-11, RF-12)."
        ),
    },
    {
        "name": "Catálogos",
        "description": (
            "Catálogos maestros de solo lectura: tipos de cuenta, rubros de "
            "estado financiero y tipos de asiento (RF-04, RF-08)."
        ),
    },
    {
        "name": "Plan de Cuentas",
        "description": (
            "Gestión del plan de cuentas jerárquico recursivo por empresa y "
            "control de cuentas hoja (RF-03, RF-04, RF-05, RF-15)."
        ),
    },
    {
        "name": "Terceros",
        "description": (
            "Registro y consulta de clientes, proveedores y otros terceros por "
            "empresa (RF-10)."
        ),
    },
    {
        "name": "Centros de Costo",
        "description": "Registro y consulta de centros de costo por empresa (RF-10).",
    },
    {
        "name": "Asientos",
        "description": (
            "Registro, modificación en borrador y contabilización de asientos "
            "con control de partida doble (RF-06, RF-07, RF-08, RF-09, RF-12, RF-15)."
        ),
    },
    {
        "name": "Reportes",
        "description": (
            "Cálculo dinámico del Estado de Resultados por periodo y del "
            "Balance General a fecha de corte (RF-13, RF-14, RF-15)."
        ),
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Administra el ciclo de vida del pool de conexiones de PostgreSQL."""
    settings = obtener_settings()
    configurar_logging(settings.log_level)
    gestor_bd = GestorBaseDatos(settings)
    await gestor_bd.iniciar_pool()
    app.state.db = gestor_bd
    try:
        yield
    finally:
        await gestor_bd.cerrar_pool()


def _registrar_manejadores_excepciones(app: FastAPI) -> None:
    """Registra la traducción de excepciones de dominio a códigos HTTP estándar."""

    @app.exception_handler(NoEncontrado)
    async def manejar_no_encontrado(
        _request: Request, exc: NoEncontrado
    ) -> JSONResponse:
        cuerpo = ErrorResponse(
            codigo="NO_ENCONTRADO", mensaje=exc.mensaje, detalle=exc.detalle
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=cuerpo.model_dump(),
        )

    @app.exception_handler(Conflicto)
    async def manejar_conflicto(_request: Request, exc: Conflicto) -> JSONResponse:
        cuerpo = ErrorResponse(
            codigo="CONFLICTO", mensaje=exc.mensaje, detalle=exc.detalle
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=cuerpo.model_dump(),
        )

    @app.exception_handler(ReglaDeNegocio)
    async def manejar_regla_negocio(
        _request: Request, exc: ReglaDeNegocio
    ) -> JSONResponse:
        cuerpo = ErrorResponse(
            codigo="REGLA_DE_NEGOCIO", mensaje=exc.mensaje, detalle=exc.detalle
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=cuerpo.model_dump(),
        )

    @app.exception_handler(SqlNoDefinido)
    async def manejar_sql_no_definido(
        _request: Request, exc: SqlNoDefinido
    ) -> JSONResponse:
        cuerpo = ErrorResponse(
            codigo="SQL_NO_DEFINIDO", mensaje=exc.mensaje, detalle=exc.detalle
        )
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=cuerpo.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def manejar_error_validacion(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        cuerpo = ErrorResponse(
            codigo="ERROR_VALIDACION",
            mensaje="Los datos de entrada no cumplen con el esquema esperado.",
            detalle=str(exc.errors()),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=cuerpo.model_dump(),
        )

    @app.exception_handler(Exception)
    async def manejar_error_inesperado(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Error inesperado procesando la solicitud: %s", exc)
        cuerpo = ErrorResponse(
            codigo="ERROR_INTERNO",
            mensaje="Ocurrió un error interno inesperado en el servidor.",
            detalle=None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=cuerpo.model_dump(),
        )


def create_app() -> FastAPI:
    """Construye y configura la instancia principal de la aplicación FastAPI."""
    settings = obtener_settings()
    configurar_logging(settings.log_level)

    aplicacion = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=(
            "API REST del Sistema Contable (Balance General y Estado de Resultados) "
            "para pymes — Universidad El Bosque · Ingeniería de Sistemas · Bases de "
            "Datos 1."
            "Expone el modelo contable normalizado en 3FN (12 entidades) con "
            "validación"
            "de partida doble, control de periodos y cálculo dinámico de reportes."
        ),
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["*"],
    )

    _registrar_manejadores_excepciones(aplicacion)
    aplicacion.include_router(health.router)
    aplicacion.include_router(api_v1_router)

    return aplicacion


app = create_app()
