"""Endpoints para catálogos de solo lectura: tipos de cuenta, rubros y tipos de asiento
(RF-04, RF-08).
"""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, CatalogoServiceDep
from app.schemas.catalogos import (
    RubroEstadoOut,
    TipoAsientoOut,
    TipoCuentaOut,
    TipoEstadoFinanciero,
)

router = APIRouter(tags=["Catálogos"])


@router.get(
    "/tipos-cuenta",
    response_model=list[TipoCuentaOut],
    status_code=status.HTTP_200_OK,
    summary="Listar tipos de cuenta contable",
    description=(
        "Retorna las 6 clases contables del catálogo TIPO_CUENTA (ACTIVO, PASIVO, "
        "PATRIMONIO, INGRESO, COSTO, GASTO) junto con su naturaleza DEBITO/CREDITO "
        "(RF-04)."
    ),
    responses={501: RESPUESTAS_ERROR_ESTANDAR[501]},
)
async def listar_tipos_cuenta(
    servicio: CatalogoServiceDep,
) -> list[TipoCuentaOut]:
    """Obtiene todos los tipos de cuenta configurados."""
    return await servicio.listar_tipos_cuenta()


@router.get(
    "/rubros-estado",
    response_model=list[RubroEstadoOut],
    status_code=status.HTTP_200_OK,
    summary="Listar rubros de estados financieros",
    description=(
        "Retorna la jerarquía de rubros de presentación (RUBRO_ESTADO) para el "
        "Balance General y el Estado de Resultados, opcionalmente filtrada por "
        "reporte (RF-04, S-11)."
    ),
    responses={501: RESPUESTAS_ERROR_ESTANDAR[501]},
)
async def listar_rubros_estado(
    servicio: CatalogoServiceDep,
    estado_financiero: Annotated[
        TipoEstadoFinanciero | None,
        Query(
            description=(
                "Filtra los rubros por reporte financiero (BALANCE o RESULTADOS)"
            )
        ),
    ] = None,
) -> list[RubroEstadoOut]:
    """Obtiene el catálogo de rubros de estado financiero."""
    return await servicio.listar_rubros_estado(estado_financiero)


@router.get(
    "/tipos-asiento",
    response_model=list[TipoAsientoOut],
    status_code=status.HTTP_200_OK,
    summary="Listar tipos de asiento contable",
    description=(
        "Retorna el catálogo TIPO_ASIENTO (APERTURA, DIARIO, AJUSTE, CIERRE) "
        "para clasificar los comprobantes registrados (RF-08)."
    ),
    responses={501: RESPUESTAS_ERROR_ESTANDAR[501]},
)
async def listar_tipos_asiento(
    servicio: CatalogoServiceDep,
) -> list[TipoAsientoOut]:
    """Obtiene los tipos de asiento disponibles."""
    return await servicio.listar_tipos_asiento()
