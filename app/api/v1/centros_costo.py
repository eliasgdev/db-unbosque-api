"""Endpoints para gestión de centros de costo por empresa (RF-10)."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, CentroCostoServiceDep
from app.schemas.centro_costo import CentroCostoCreate, CentroCostoOut

router = APIRouter(tags=["Centros de Costo"])


@router.post(
    "/empresas/{id_empresa}/centros-costo",
    response_model=CentroCostoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar centro de costo en una empresa",
    description=(
        "Registra un centro de costo asociado a una empresa para imputación "
        "opcional en los movimientos de un asiento (RF-10)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_centro_costo(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    datos: CentroCostoCreate,
    servicio: CentroCostoServiceDep,
) -> CentroCostoOut:
    """Crea un nuevo centro de costo vinculado a la empresa."""
    return await servicio.crear_centro_costo(id_empresa, datos)


@router.get(
    "/empresas/{id_empresa}/centros-costo",
    response_model=list[CentroCostoOut],
    status_code=status.HTTP_200_OK,
    summary="Listar centros de costo de una empresa",
    description=(
        "Devuelve todos los centros de costo registrados para la empresa (RF-10)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def listar_centros_costo_empresa(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    servicio: CentroCostoServiceDep,
) -> list[CentroCostoOut]:
    """Lista los centros de costo de una empresa."""
    return await servicio.listar_centros_costo_empresa(id_empresa)
