"""Endpoint operativo de estado y salud del servicio (/health)."""

from fastapi import APIRouter, status

from app.api.deps import HealthServiceDep
from app.schemas.comun import HealthResponse

router = APIRouter(tags=["Operación"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar estado de la API y conexión a PostgreSQL",
    description=(
        "Devuelve el estado operativo del backend, el entorno activo y el "
        "resultado de la comprobación contra el pool de PostgreSQL."
    ),
)
async def verificar_salud(servicio: HealthServiceDep) -> HealthResponse:
    """Ejecuta la verificación operativa del servicio y de la base de datos."""
    return await servicio.verificar_estado()
