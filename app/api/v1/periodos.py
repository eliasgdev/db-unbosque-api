"""Endpoints para gestión de periodos contables y cierre de periodo (RF-02, RF-11,
RF-12,
RF-15).
"""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, PeriodoServiceDep
from app.schemas.periodo import (
    CierrePeriodoCreate,
    CierrePeriodoOut,
    PeriodoCreate,
    PeriodoOut,
)

router = APIRouter(tags=["Periodos"])


@router.post(
    "/empresas/{id_empresa}/periodos",
    response_model=PeriodoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear periodo contable para una empresa",
    description=(
        "Abre un nuevo periodo contable verificando que fecha_fin > fecha_inicio "
        "y que el intervalo no se traslape con otro periodo de la misma empresa "
        "(RF-02, S-13)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_periodo(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    datos: PeriodoCreate,
    servicio: PeriodoServiceDep,
) -> PeriodoOut:
    """Registra un nuevo periodo contable en estado ABIERTO."""
    return await servicio.crear_periodo(id_empresa, datos)


@router.get(
    "/empresas/{id_empresa}/periodos",
    response_model=list[PeriodoOut],
    status_code=status.HTTP_200_OK,
    summary="Listar periodos contables de una empresa",
    description=(
        "Devuelve todos los periodos contables (abiertos y cerrados) de una empresa "
        "(RF-02, RF-15)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def listar_periodos_empresa(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    servicio: PeriodoServiceDep,
) -> list[PeriodoOut]:
    """Lista los periodos asociados a una empresa."""
    return await servicio.listar_periodos_empresa(id_empresa)


@router.get(
    "/periodos/{id_periodo}",
    response_model=PeriodoOut,
    status_code=status.HTTP_200_OK,
    summary="Consultar periodo contable por ID",
    description=(
        "Obtiene los detalles y el estado (ABIERTO/CERRADO) de un periodo contable "
        "(RF-02, RF-15)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_periodo(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador único del periodo contable")
    ],
    servicio: PeriodoServiceDep,
) -> PeriodoOut:
    """Consulta un periodo contable específico."""
    return await servicio.obtener_periodo(id_periodo)


@router.post(
    "/periodos/{id_periodo}/cierre",
    response_model=CierrePeriodoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cerrar periodo contable y generar asiento de cierre",
    description=(
        "Calcula la utilidad o pérdida neta del periodo, genera el asiento "
        "automático de tipo CIERRE trasladando el resultado a la cuenta de "
        "patrimonio indicada y cambia el estado del periodo a CERRADO en una "
        "sola transacción atómica (RF-11, RF-12, S-16, S-17)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def cerrar_periodo(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador del periodo a cerrar")
    ],
    datos: CierrePeriodoCreate,
    servicio: PeriodoServiceDep,
) -> CierrePeriodoOut:
    """Ejecuta el cierre definitivo de un periodo contable abierto."""
    return await servicio.cerrar_periodo(id_periodo, datos)


@router.get(
    "/periodos/{id_periodo}/cierre",
    response_model=CierrePeriodoOut,
    status_code=status.HTTP_200_OK,
    summary="Consultar cierre y utilidad trasladada de un periodo",
    description=(
        "Devuelve los datos del registro CIERRE_PERIODO, incluyendo el "
        "asiento de cierre generado y la utilidad o pérdida neta trasladada (RF-11)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_cierre_periodo(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador del periodo consultado")
    ],
    servicio: PeriodoServiceDep,
) -> CierrePeriodoOut:
    """Obtiene la información del cierre ejecutado sobre un periodo."""
    return await servicio.obtener_cierre_periodo(id_periodo)
