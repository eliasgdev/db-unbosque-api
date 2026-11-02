"""Endpoints para registro, edición, consulta y contabilización de asientos (RF-06..09,
12,
15).
"""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, AsientoServiceDep
from app.schemas.asiento import (
    AsientoCreate,
    AsientoDetalleOut,
    AsientoResumenOut,
    AsientoUpdate,
)

router = APIRouter(tags=["Asientos"])


@router.post(
    "/periodos/{id_periodo}/asientos",
    response_model=AsientoDetalleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asiento con movimientos en borrador",
    description=(
        "Registra un nuevo asiento contable en estado BORRADOR dentro de un "
        "periodo ABIERTO, verificando que la fecha pertenezca al periodo y que "
        "todas las cuentas imputadas sean hojas de la misma empresa (RF-05, RF-06, "
        "RF-08, RF-12)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def crear_asiento(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador del periodo contable")
    ],
    datos: AsientoCreate,
    servicio: AsientoServiceDep,
) -> AsientoDetalleOut:
    """Crea un asiento contable y sus movimientos en estado BORRADOR."""
    return await servicio.crear_asiento(id_periodo, datos)


@router.get(
    "/periodos/{id_periodo}/asientos",
    response_model=list[AsientoResumenOut],
    status_code=status.HTTP_200_OK,
    summary="Listar asientos de un periodo contable",
    description=(
        "Devuelve la lista resumida de los asientos registrados en un periodo "
        "contable con sus totales débito y crédito (RF-15)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def listar_asientos_periodo(
    id_periodo: Annotated[
        int, Path(gt=0, description="Identificador del periodo contable")
    ],
    servicio: AsientoServiceDep,
) -> list[AsientoResumenOut]:
    """Lista los asientos de un periodo."""
    return await servicio.listar_asientos_periodo(id_periodo)


@router.get(
    "/asientos/{id_asiento}",
    response_model=AsientoDetalleOut,
    status_code=status.HTTP_200_OK,
    summary="Consultar detalle de asiento con sus movimientos",
    description=(
        "Devuelve la cabecera del asiento junto con todos sus renglones de "
        "movimiento débito/crédito y el indicador de cuadre (RF-15)."
    ),
    responses={
        404: RESPUESTAS_ERROR_ESTANDAR[404],
        501: RESPUESTAS_ERROR_ESTANDAR[501],
    },
)
async def obtener_asiento(
    id_asiento: Annotated[
        int, Path(gt=0, description="Identificador único del asiento contable")
    ],
    servicio: AsientoServiceDep,
) -> AsientoDetalleOut:
    """Obtiene el detalle completo de un asiento."""
    return await servicio.obtener_asiento(id_asiento)


@router.put(
    "/asientos/{id_asiento}",
    response_model=AsientoDetalleOut,
    status_code=status.HTTP_200_OK,
    summary="Modificar asiento en borrador de un periodo abierto",
    description=(
        "Actualiza la cabecera y reemplaza los movimientos de un asiento que "
        "aún se encuentre en estado BORRADOR y cuyo periodo esté ABIERTO (RF-12)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def actualizar_asiento(
    id_asiento: Annotated[
        int, Path(gt=0, description="Identificador del asiento a modificar")
    ],
    datos: AsientoUpdate,
    servicio: AsientoServiceDep,
) -> AsientoDetalleOut:
    """Modifica un asiento en estado BORRADOR."""
    return await servicio.actualizar_asiento(id_asiento, datos)


@router.post(
    "/asientos/{id_asiento}/contabilizar",
    response_model=AsientoDetalleOut,
    status_code=status.HTTP_200_OK,
    summary="Validar partida doble y contabilizar asiento",
    description=(
        "Verifica que el periodo esté ABIERTO y que la suma de débitos sea "
        "exactamente igual a la suma de créditos (Σ debe = Σ haber > 0). "
        "Si cumple, cambia el estado del asiento a CONTABILIZADO para que sea "
        "incluido en los estados financieros (RF-07, RF-09, S-01)."
    ),
    responses=RESPUESTAS_ERROR_ESTANDAR,
)
async def contabilizar_asiento(
    id_asiento: Annotated[
        int, Path(gt=0, description="Identificador del asiento a contabilizar")
    ],
    servicio: AsientoServiceDep,
) -> AsientoDetalleOut:
    """Contabiliza un asiento en borrador tras validar partida doble."""
    return await servicio.contabilizar_asiento(id_asiento)
