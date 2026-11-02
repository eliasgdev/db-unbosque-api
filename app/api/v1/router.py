"""Enrutador principal de la versión 1 de la API (/api/v1)."""

from fastapi import APIRouter

from app.api.v1 import (
    asientos,
    catalogos,
    centros_costo,
    cuentas,
    empresas,
    health,
    monedas,
    periodos,
    reportes,
    terceros,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router)
api_v1_router.include_router(monedas.router)
api_v1_router.include_router(empresas.router)
api_v1_router.include_router(periodos.router)
api_v1_router.include_router(catalogos.router)
api_v1_router.include_router(cuentas.router)
api_v1_router.include_router(terceros.router)
api_v1_router.include_router(centros_costo.router)
api_v1_router.include_router(asientos.router)
api_v1_router.include_router(reportes.router)
