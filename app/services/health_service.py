"""Servicio de diagnóstico y salud operativa de la API y PostgreSQL."""

from typing import Literal

from app.core.config import Settings
from app.core.database import GestorBaseDatos
from app.core.exceptions import SqlNoDefinido
from app.core.logging import obtener_logger
from app.repositories.health_repository import HealthRepository
from app.schemas.comun import HealthResponse

logger = obtener_logger(__name__)


class HealthService:
    """Verifica el estado del servicio y la conectividad con PostgreSQL."""

    def __init__(
        self,
        db: GestorBaseDatos,
        settings: Settings,
        health_repo: HealthRepository,
    ) -> None:
        """Inicializa el servicio de salud con sus dependencias."""
        self._db = db
        self._settings = settings
        self._health_repo = health_repo

    async def verificar_estado(self) -> HealthResponse:
        """Comprueba el estado de la API y de la base de datos sin propagar fallo

        501.
        """
        estado_bd: Literal["conectada", "sql_no_definido", "sin_conexion"] = "conectada"
        estado_general: Literal["ok", "degradado"] = "ok"

        try:
            async with self._db.conexion() as sesion:
                await self._health_repo.verificar_conexion(sesion)
        except SqlNoDefinido:
            estado_bd = "sql_no_definido"
        except Exception as exc:
            logger.warning("Fallo al verificar conexión con PostgreSQL: %s", exc)
            estado_bd = "sin_conexion"
            estado_general = "degradado"

        return HealthResponse(
            estado=estado_general,
            servicio=self._settings.app_name,
            entorno=self._settings.app_env,
            base_datos=estado_bd,
        )
