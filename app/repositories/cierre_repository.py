"""Repositorio de acceso a datos para la entidad CIERRE_PERIODO (RF-11)."""

from datetime import datetime
from decimal import Decimal

from app.core.database import FilaDict, SesionBD, ejecutar_consulta_uno

# Propósito: registrar el cierre definitivo de un periodo contable y su utilidad.
# Parámetros: id_periodo (int), id_asiento_cierre (int | None),
#             utilidad_neta (Decimal), fecha_cierre (datetime).
# Retorna: la fila insertada de CIERRE_PERIODO.
# Tablas: CIERRE_PERIODO.
_SQL_CREAR_CIERRE = """
INSERT INTO cierre_periodo (
    id_periodo,
    id_asiento_cierre,
    utilidad_neta,
    fecha_cierre
)
VALUES (
    %(id_periodo)s,
    %(id_asiento_cierre)s,
    %(utilidad_neta)s,
    %(fecha_cierre)s
)
RETURNING
    id_cierre,
    id_periodo,
    id_asiento_cierre,
    utilidad_neta,
    fecha_cierre;
"""

# Propósito: consultar el registro de cierre asociado a un periodo contable.
#            Usa LEFT JOIN hacia ASIENTO porque id_asiento_cierre es anulable
#            cuando un periodo se cierra sin movimientos de resultado.
# Parámetros: id_periodo (int).
# Retorna: una fila de CIERRE_PERIODO o ninguna.
# Tablas: CIERRE_PERIODO, PERIODO_CONTABLE, ASIENTO.
_SQL_OBTENER_POR_PERIODO = """
SELECT
    cp.id_cierre,
    cp.id_periodo,
    cp.id_asiento_cierre,
    cp.utilidad_neta,
    cp.fecha_cierre
FROM cierre_periodo cp
INNER JOIN periodo_contable p ON p.id_periodo = cp.id_periodo
LEFT JOIN asiento a ON a.id_asiento = cp.id_asiento_cierre
WHERE cp.id_periodo = %(id_periodo)s;
"""


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
