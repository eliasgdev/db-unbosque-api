"""Repositorio de acceso a datos para la entidad MOVIMIENTO (RF-06, RF-07, RF-10,

RF-15).
"""

from decimal import Decimal

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_comando,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: insertar un renglón de movimiento débito o crédito asociado a un asiento.
# Parámetros: id_asiento (int), id_cuenta (int), id_tercero (int | None),
#   id_centro_costo (int | None), debe (Decimal), haber (Decimal).
# Retorna: la fila insertada de MOVIMIENTO.
# Tablas: MOVIMIENTO.
_SQL_CREAR_MOVIMIENTO = """"""

# Propósito: listar todos los movimientos de un asiento junto con el código y nombre de
#   la cuenta.
# Parámetros: id_asiento (int).
# Retorna: lista de filas de MOVIMIENTO enriquecidas con codigo_cuenta y nombre_cuenta.
# Tablas: MOVIMIENTO, PLAN_CUENTA, TERCERO, CENTRO_COSTO.
_SQL_LISTAR_POR_ASIENTO = """"""

# Propósito: eliminar los movimientos existentes de un asiento en estado BORRADOR antes
#   de reemplazarlos.
# Parámetros: id_asiento (int).
# Retorna: número de filas eliminadas.
# Tablas: MOVIMIENTO.
_SQL_ELIMINAR_POR_ASIENTO = """"""


class MovimientoRepository:
    """Operaciones de persistencia y consulta para los movimientos de un asiento."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_asiento: int,
        id_cuenta: int,
        id_tercero: int | None,
        id_centro_costo: int | None,
        debe: Decimal,
        haber: Decimal,
    ) -> FilaDict | None:
        """Inserta un movimiento contable asociado al asiento."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_MOVIMIENTO,
            {
                "id_asiento": id_asiento,
                "id_cuenta": id_cuenta,
                "id_tercero": id_tercero,
                "id_centro_costo": id_centro_costo,
                "debe": debe,
                "haber": haber,
            },
            operacion="movimiento_repository._SQL_CREAR_MOVIMIENTO",
        )

    async def listar_por_asiento(
        self, sesion: SesionBD, id_asiento: int
    ) -> list[FilaDict]:
        """Obtiene la lista de movimientos pertenecientes a un asiento."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_ASIENTO,
            {"id_asiento": id_asiento},
            operacion="movimiento_repository._SQL_LISTAR_POR_ASIENTO",
        )

    async def eliminar_por_asiento(self, sesion: SesionBD, id_asiento: int) -> int:
        """Elimina los movimientos asociados a un asiento en borrador."""
        return await ejecutar_comando(
            sesion,
            _SQL_ELIMINAR_POR_ASIENTO,
            {"id_asiento": id_asiento},
            operacion="movimiento_repository._SQL_ELIMINAR_POR_ASIENTO",
        )
