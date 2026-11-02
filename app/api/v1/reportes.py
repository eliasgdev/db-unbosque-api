"""Endpoints para consultar el Estado de Resultados y el Balance General (RF-13, RF-14,
RF-15).
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, ReporteServiceDep
from app.schemas.reportes import BalanceGeneralOut, EstadoResultadosOut

router = APIRouter(tags=["Reportes"])


@router.get(
    "/periodos/{id_periodo}/estado-resultados",
    response_model=EstadoResultadosOut,
    status_code=status.HTTP_200_OK,
    summary="Generar Estado de Resultados de un periodo",
    description=(
        "Calcula dinámicamente (sin almacenar saldos) los ingresos, costos, "
        "gastos, utilidad bruta, utilidad operacional y utilidad neta de un "
        "periodo contable a partir de los asientos en estado CONTABILIZADO, "
        "estructurados según RUBRO_ESTADO (RF-09, RF-13, RF-15, S-07, S-10, S-11)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_estado_resultados(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador del periodo contable")
    ],
    servicio: ReporteServiceDep,
) -> EstadoResultadosOut:
    """Genera el Estado de Resultados del periodo solicitado."""
    return await servicio.generar_estado_resultados(id_periodo)


@router.get(
    "/empresas/{id_empresa}/balance-general",
    response_model=BalanceGeneralOut,
    status_code=status.HTTP_200_OK,
    summary="Generar Balance General a fecha de corte",
    description=(
        "Calcula dinámicamente el Balance General agrupado por rubros de "
        "RUBRO_ESTADO hasta la fecha_corte indicada, integrando la utilidad "
        "del ejercicio en el patrimonio y verificando el cumplimiento de la "
        "ecuación contable Activo = Pasivo + Patrimonio (RF-09, RF-14, RF-15, S-07, "
        "S-09, S-11)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        422: RESPUESTAS_ERROR_ESTANDAR[422],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_balance_general(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    fecha_corte: Annotated[
        date,
        Query(
            description=(
                "Fecha de corte (YYYY-MM-DD) para acumular los saldos contabilizados"
            ),
            examples=["2026-12-31"],
        ),
    ],
    servicio: ReporteServiceDep,
) -> BalanceGeneralOut:
    """Genera el Balance General de la empresa a la fecha de corte."""
    return await servicio.generar_balance_general(id_empresa, fecha_corte)
