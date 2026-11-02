"""Endpoints para gestión de terceros por empresa (RF-10)."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, TerceroServiceDep
from app.schemas.tercero import TerceroCreate, TerceroOut

router = APIRouter(tags=["Terceros"])


@router.post(
    "/empresas/{id_empresa}/terceros",
    response_model=TerceroOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar tercero en una empresa",
    description=(
        "Registra un tercero (CLIENTE, PROVEEDOR u OTRO) asociado a una empresa "
        "para su imputación opcional en movimientos contables (RF-10)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_tercero(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    datos: TerceroCreate,
    servicio: TerceroServiceDep,
) -> TerceroOut:
    """Crea un nuevo tercero vinculado a la empresa."""
    return await servicio.crear_tercero(id_empresa, datos)


@router.get(
    "/empresas/{id_empresa}/terceros",
    response_model=list[TerceroOut],
    status_code=status.HTTP_200_OK,
    summary="Listar terceros de una empresa",
    description=(
        "Devuelve todos los terceros registrados para la empresa indicada (RF-10)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def listar_terceros_empresa(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    servicio: TerceroServiceDep,
) -> list[TerceroOut]:
    """Lista los terceros pertenecientes a una empresa."""
    return await servicio.listar_terceros_empresa(id_empresa)
