"""Endpoints para consulta del catálogo de monedas (RF-01)."""

from fastapi import APIRouter, status

from app.api.deps import RESPUESTAS_ERROR_ESTANDAR, CatalogoServiceDep
from app.schemas.moneda import MonedaOut

router = APIRouter(tags=["Monedas"])


@router.get(
    "/monedas",
    response_model=list[MonedaOut],
    status_code=status.HTTP_200_OK,
    summary="Listar catálogo de monedas",
    description=(
        "Retorna todas las monedas registradas en el catálogo MONEDA que pueden "
        "asignarse como moneda funcional base al registrar una empresa (RF-01)."
    ),
    responses={501: RESPUESTAS_ERROR_ESTANDAR[501]},
)
async def listar_monedas(servicio: CatalogoServiceDep) -> list[MonedaOut]:
    """Obtiene la lista de monedas disponibles en el sistema."""
    return await servicio.listar_monedas()
