"""Inyección de dependencias para routers de FastAPI.

Provee instancias de configuración, gestor de base de datos, repositorios y
servicios de negocio, además de las respuestas de error documentadas para Swagger.
"""

from typing import Annotated, Any

from fastapi import Depends, Request

from app.core.config import Settings, obtener_settings
from app.core.database import GestorBaseDatos
from app.repositories.asiento_repository import AsientoRepository
from app.repositories.centro_costo_repository import CentroCostoRepository
from app.repositories.cierre_repository import CierreRepository
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.moneda_repository import MonedaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.rubro_estado_repository import RubroEstadoRepository
from app.repositories.tercero_repository import TerceroRepository
from app.repositories.tipo_asiento_repository import TipoAsientoRepository
from app.repositories.tipo_cuenta_repository import TipoCuentaRepository
from app.schemas.comun import ErrorResponse
from app.services.asiento_service import AsientoService
from app.services.catalogo_service import CatalogoService
from app.services.centro_costo_service import CentroCostoService
from app.services.cuenta_service import CuentaService
from app.services.empresa_service import EmpresaService
from app.services.health_service import HealthService
from app.services.periodo_service import PeriodoService
from app.services.reporte_service import ReporteService
from app.services.tercero_service import TerceroService

RESPUESTAS_ERROR_ESTANDAR: dict[int | str, dict[str, Any]] = {
    404: {
        "model": ErrorResponse,
        "description": "Recurso o entidad contable no encontrada",
    },
    409: {
        "model": ErrorResponse,
        "description": (
            "Conflicto de estado o unicidad (duplicado, traslape o periodo cerrado)"
        ),
    },
    422: {
        "model": ErrorResponse,
        "description": "Violación de regla contable o error de validación de datos",
    },
    501: {
        "model": ErrorResponse,
        "description": (
            "Sentencia SQL vacía pendiente de definición manual en el repositorio"
        ),
    },
}


def obtener_db(request: Request) -> GestorBaseDatos:
    """Extrae el gestor de base de datos inicializado en el estado de la aplicación."""
    db: GestorBaseDatos = request.app.state.db
    return db


SettingsDep = Annotated[Settings, Depends(obtener_settings)]
DbDep = Annotated[GestorBaseDatos, Depends(obtener_db)]


def obtener_health_service(db: DbDep, settings: SettingsDep) -> HealthService:
    """Construye el servicio de verificación de salud."""
    return HealthService(db=db, settings=settings, health_repo=HealthRepository())


def obtener_catalogo_service(db: DbDep) -> CatalogoService:
    """Construye el servicio de catálogos de solo lectura."""
    return CatalogoService(
        db=db,
        moneda_repo=MonedaRepository(),
        tipo_cuenta_repo=TipoCuentaRepository(),
        rubro_repo=RubroEstadoRepository(),
        tipo_asiento_repo=TipoAsientoRepository(),
    )


def obtener_empresa_service(db: DbDep) -> EmpresaService:
    """Construye el servicio de gestión de empresas."""
    return EmpresaService(
        db=db,
        empresa_repo=EmpresaRepository(),
        moneda_repo=MonedaRepository(),
    )


def obtener_periodo_service(db: DbDep) -> PeriodoService:
    """Construye el servicio de gestión y cierre de periodos contables."""
    return PeriodoService(
        db=db,
        periodo_repo=PeriodoRepository(),
        empresa_repo=EmpresaRepository(),
        cierre_repo=CierreRepository(),
        cuenta_repo=CuentaRepository(),
        asiento_repo=AsientoRepository(),
        movimiento_repo=MovimientoRepository(),
        tipo_asiento_repo=TipoAsientoRepository(),
        reporte_repo=ReporteRepository(),
    )


def obtener_cuenta_service(db: DbDep) -> CuentaService:
    """Construye el servicio del plan de cuentas jerárquico."""
    return CuentaService(
        db=db,
        cuenta_repo=CuentaRepository(),
        empresa_repo=EmpresaRepository(),
        tipo_cuenta_repo=TipoCuentaRepository(),
        rubro_repo=RubroEstadoRepository(),
    )


def obtener_tercero_service(db: DbDep) -> TerceroService:
    """Construye el servicio de gestión de terceros."""
    return TerceroService(
        db=db,
        tercero_repo=TerceroRepository(),
        empresa_repo=EmpresaRepository(),
    )


def obtener_centro_costo_service(db: DbDep) -> CentroCostoService:
    """Construye el servicio de gestión de centros de costo."""
    return CentroCostoService(
        db=db,
        centro_costo_repo=CentroCostoRepository(),
        empresa_repo=EmpresaRepository(),
    )


def obtener_asiento_service(db: DbDep) -> AsientoService:
    """Construye el servicio de gestión y contabilización de asientos."""
    return AsientoService(
        db=db,
        asiento_repo=AsientoRepository(),
        movimiento_repo=MovimientoRepository(),
        periodo_repo=PeriodoRepository(),
        tipo_asiento_repo=TipoAsientoRepository(),
        cuenta_repo=CuentaRepository(),
        tercero_repo=TerceroRepository(),
        centro_costo_repo=CentroCostoRepository(),
    )


def obtener_reporte_service(db: DbDep) -> ReporteService:
    """Construye el servicio de generación de Balance General y Estado de Resultados."""
    return ReporteService(
        db=db,
        reporte_repo=ReporteRepository(),
        periodo_repo=PeriodoRepository(),
        empresa_repo=EmpresaRepository(),
        rubro_repo=RubroEstadoRepository(),
    )


HealthServiceDep = Annotated[HealthService, Depends(obtener_health_service)]
CatalogoServiceDep = Annotated[CatalogoService, Depends(obtener_catalogo_service)]
EmpresaServiceDep = Annotated[EmpresaService, Depends(obtener_empresa_service)]
PeriodoServiceDep = Annotated[PeriodoService, Depends(obtener_periodo_service)]
CuentaServiceDep = Annotated[CuentaService, Depends(obtener_cuenta_service)]
TerceroServiceDep = Annotated[TerceroService, Depends(obtener_tercero_service)]
CentroCostoServiceDep = Annotated[
    CentroCostoService, Depends(obtener_centro_costo_service)
]
AsientoServiceDep = Annotated[AsientoService, Depends(obtener_asiento_service)]
ReporteServiceDep = Annotated[ReporteService, Depends(obtener_reporte_service)]
