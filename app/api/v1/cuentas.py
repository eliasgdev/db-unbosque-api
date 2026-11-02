"""Endpoints para gestión del Plan de Cuentas jerárquico por empresa (RF-03, RF-04,
RF-05,
RF-15).
"""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, CuentaServiceDep
from app.schemas.cuenta import CuentaArbolOut, CuentaCreate, CuentaOut

router = APIRouter(tags=["Plan de Cuentas"])


@router.post(
    "/empresas/{id_empresa}/cuentas",
    response_model=CuentaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cuenta en el plan contable de una empresa",
    description=(
        "Registra una nueva cuenta en PLAN_CUENTA asociada a una empresa, un "
        "tipo de cuenta, un rubro de estado financiero y opcionalmente una "
        "cuenta padre de la misma empresa (RF-03, RF-04, RF-05)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_cuenta(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    datos: CuentaCreate,
    servicio: CuentaServiceDep,
) -> CuentaOut:
    """Da de alta una nueva cuenta en el plan de la empresa."""
    return await servicio.crear_cuenta(id_empresa, datos)


@router.get(
    "/empresas/{id_empresa}/cuentas",
    response_model=list[CuentaArbolOut],
    status_code=status.HTTP_200_OK,
    summary="Consultar plan de cuentas jerárquico de una empresa",
    description=(
        "Devuelve el árbol jerárquico completo del plan de cuentas de una "
        "empresa, anidando las subcuentas recursivamente (RF-03, RF-15)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def listar_plan_cuentas(
    id_empresa: Annotated[
        int, Path(gt=0, description="Identificador único de la empresa")
    ],
    servicio: CuentaServiceDep,
) -> list[CuentaArbolOut]:
    """Obtiene el árbol del plan de cuentas de la empresa."""
    return await servicio.listar_plan_cuentas(id_empresa)


@router.get(
    "/cuentas/{id_cuenta}",
    response_model=CuentaOut,
    status_code=status.HTTP_200_OK,
    summary="Consultar detalle de una cuenta por ID",
    description=(
        "Obtiene los atributos de una cuenta específica del plan contable (RF-03)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_cuenta(
    id_cuenta: Annotated[
        int, Path(gt=0, description="Identificador único de la cuenta contable")
    ],
    servicio: CuentaServiceDep,
) -> CuentaOut:
    """Consulta una cuenta contable por su identificador."""
    return await servicio.obtener_cuenta(id_cuenta)
