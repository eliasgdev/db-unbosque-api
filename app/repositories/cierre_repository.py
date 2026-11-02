"""Repositorio de acceso a datos para la entidad CIERRE_PERIODO (RF-11)."""

from datetime import datetime
from decimal import Decimal

from app.core.database import FilaDict, SesionBD, ejecutar_consulta_uno

# Propósito: registrar el cierre definitivo de un periodo contable y su utilidad neta.
# Parámetros: id_periodo (int), id_asiento_cierre (int | None), utilidad_neta (Decimal),
#   fecha_cierre (datetime).
# Retorna: la fila insertada de CIERRE_PERIODO.
# Tablas: CIERRE_PERIODO.
_SQL_CREAR_CIERRE = """"""

# Propósito: consultar el registro de cierre asociado a un periodo contable.
# Parámetros: id_periodo (int).
# Retorna: una fila de CIERRE_PERIODO o ninguna.
# Tablas: CIERRE_PERIODO, PERIODO_CONTABLE, ASIENTO.
_SQL_OBTENER_POR_PERIODO = """"""


class CierreRepository:
    """Operaciones de persistencia y consulta para CIERRE_PERIODO."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_periodo: int,
        id_asiento_cierre: int | None,
        utilidad_neta: Decimal,
        fecha_cierre: datetime,
    ) -> FilaDict | None:
        """Inserta el registro de cierre del periodo contable."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_CIERRE,
            {
                "id_periodo": id_periodo,
                "id_asiento_cierre": id_asiento_cierre,
                "utilidad_neta": utilidad_neta,
                "fecha_cierre": fecha_cierre,
            },
            operacion="cierre_repository._SQL_CREAR_CIERRE",
        )

    async def obtener_por_periodo(
        self, sesion: SesionBD, id_periodo: int
    ) -> FilaDict | None:
        """Obtiene el cierre registrado para un periodo dado."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_PERIODO,
            {"id_periodo": id_periodo},
            operacion="cierre_repository._SQL_OBTENER_POR_PERIODO",
        )
