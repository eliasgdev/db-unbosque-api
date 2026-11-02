"""Endpoints para el alta y consulta de empresas (RF-01)."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, EmpresaServiceDep
from app.schemas.empresa import EmpresaCreate, EmpresaOut

router = APIRouter(tags=["Empresas"])


@router.post(
    "/empresas",
    response_model=EmpresaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva empresa",
    description=(
        "Registra una empresa con su NIT único, razón social y moneda base "
        "asociada al catálogo MONEDA (RF-01)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_empresa(
    datos: EmpresaCreate,
    servicio: EmpresaServiceDep,
) -> EmpresaOut:
    """Crea una nueva empresa en el sistema contable."""
    return await servicio.crear_empresa(datos)


@router.get(
    "/empresas",
    response_model=list[EmpresaOut],
    status_code=status.HTTP_200_OK,
    summary="Listar empresas registradas",
    description=(
        "Obtiene el listado completo de empresas registradas en el sistema (RF-01)."
    ),
    responses={501: RESPUESTAS_ERROR_ESTANDAR[501]},
)
async def listar_empresas(servicio: EmpresaServiceDep) -> list[EmpresaOut]:
    """Retorna todas las empresas registradas."""
    return await servicio.listar_empresas()


@router.get(
    "/empresas/{id_empresa}",
    response_model=EmpresaOut,
    status_code=status.HTTP_200_OK,
    summary="Consultar empresa por ID",
    description=(
        "Devuelve la información detallada de una empresa a partir de su "
        "identificador único (RF-01)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_empresa(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    servicio: EmpresaServiceDep,
) -> EmpresaOut:
    """Consulta una empresa específica por su clave primaria."""
    return await servicio.obtener_empresa(id_empresa)
