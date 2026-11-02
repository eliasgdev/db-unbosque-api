"""Servicio de consulta para los catálogos maestros del sistema (RF-01, RF-04,

RF-08).
"""

from app.core.database import GestorBaseDatos
from app.repositories.moneda_repository import MonedaRepository
from app.repositories.rubro_estado_repository import RubroEstadoRepository
from app.repositories.tipo_asiento_repository import TipoAsientoRepository
from app.repositories.tipo_cuenta_repository import TipoCuentaRepository
from app.schemas.catalogos import (
    RubroEstadoOut,
    TipoAsientoOut,
    TipoCuentaOut,
    TipoEstadoFinanciero,
)
from app.schemas.moneda import MonedaOut


class CatalogoService:
    """Provee acceso de lectura a monedas, tipos de cuenta, rubros y tipos de

    asiento.
    """

    def __init__(
        self,
        db: GestorBaseDatos,
        moneda_repo: MonedaRepository,
        tipo_cuenta_repo: TipoCuentaRepository,
        rubro_repo: RubroEstadoRepository,
        tipo_asiento_repo: TipoAsientoRepository,
    ) -> None:
        """Inicializa el servicio de catálogos con sus repositorios."""
        self._db = db
        self._moneda_repo = moneda_repo
        self._tipo_cuenta_repo = tipo_cuenta_repo
        self._rubro_repo = rubro_repo
        self._tipo_asiento_repo = tipo_asiento_repo

    async def listar_monedas(self) -> list[MonedaOut]:
        """Retorna el catálogo completo de monedas (RF-01)."""
        async with self._db.conexion() as sesion:
            filas = await self._moneda_repo.listar(sesion)
        return [MonedaOut.model_validate(fila) for fila in filas]

    async def listar_tipos_cuenta(self) -> list[TipoCuentaOut]:
        """Retorna el catálogo de tipos de cuenta contable (RF-04)."""
        async with self._db.conexion() as sesion:
            filas = await self._tipo_cuenta_repo.listar(sesion)
        return [TipoCuentaOut.model_validate(fila) for fila in filas]

    async def listar_rubros_estado(
        self, estado_financiero: TipoEstadoFinanciero | None = None
    ) -> list[RubroEstadoOut]:
        """Retorna los rubros de estados financieros, opcionalmente filtrados

        (RF-04).
        """
        async with self._db.conexion() as sesion:
            if estado_financiero is not None:
                filas = await self._rubro_repo.listar_por_estado_financiero(
                    sesion, estado_financiero
                )
            else:
                filas = await self._rubro_repo.listar(sesion)
        return [RubroEstadoOut.model_validate(fila) for fila in filas]

    async def listar_tipos_asiento(self) -> list[TipoAsientoOut]:
        """Retorna el catálogo de tipos de asiento (RF-08)."""
        async with self._db.conexion() as sesion:
            filas = await self._tipo_asiento_repo.listar(sesion)
        return [TipoAsientoOut.model_validate(fila) for fila in filas]
