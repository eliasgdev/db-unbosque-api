"""Repositorio de acceso a datos para la entidad ASIENTO (RF-06, RF-07, RF-08, RF-12,
RF-15).
"""

from datetime import date

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: insertar la cabecera de un asiento contable dentro de un periodo.
# Parámetros: id_periodo (int), id_tipo_asiento (int), numero (int), fecha (date),
#   descripcion (str), estado (str).
# Retorna: la fila insertada de ASIENTO.
# Tablas: ASIENTO.
_SQL_CREAR_ASIENTO = """"""

# Propósito: obtener la cabecera de un asiento por su identificador junto con el nombre
#   de su tipo.
# Parámetros: id_asiento (int).
# Retorna: una fila de ASIENTO enriquecida con tipo_asiento o ninguna.
# Tablas: ASIENTO, TIPO_ASIENTO.
_SQL_OBTENER_POR_ID = """"""

# Propósito: listar los asientos de un periodo con totales calculados de debe y haber.
# Parámetros: id_periodo (int).
# Retorna: lista de filas de ASIENTO con tipo_asiento, total_debe y total_haber.
# Tablas: ASIENTO, TIPO_ASIENTO, MOVIMIENTO.
_SQL_LISTAR_POR_PERIODO = """"""

# Propósito: buscar un asiento por el par único (id_periodo, numero).
# Parámetros: id_periodo (int), numero (int).
# Retorna: una fila de ASIENTO o ninguna.
# Tablas: ASIENTO.
_SQL_OBTENER_POR_NUMERO_PERIODO = """"""

# Propósito: obtener el siguiente número consecutivo disponible para un asiento en un
#   periodo.
# Parámetros: id_periodo (int).
# Retorna: una fila con la columna siguiente_numero (int).
# Tablas: ASIENTO.
_SQL_SIGUIENTE_NUMERO_EN_PERIODO = """"""

# Propósito: actualizar los datos de cabecera de un asiento en estado BORRADOR.
# Parámetros: id_asiento (int), id_tipo_asiento (int), fecha (date), descripcion (str).
# Retorna: la fila actualizada de ASIENTO.
# Tablas: ASIENTO.
_SQL_ACTUALIZAR_CABECERA = """"""

# Propósito: cambiar el estado de un asiento (de BORRADOR a CONTABILIZADO).
# Parámetros: id_asiento (int), estado (str).
# Retorna: la fila actualizada de ASIENTO.
# Tablas: ASIENTO.
_SQL_ACTUALIZAR_ESTADO = """"""


class AsientoRepository:
    """Operaciones de persistencia y consulta para la cabecera ASIENTO."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_periodo: int,
        id_tipo_asiento: int,
        numero: int,
        fecha: date,
        descripcion: str,
        estado: str = "BORRADOR",
    ) -> FilaDict | None:
        """Inserta la cabecera de un asiento contable."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_ASIENTO,
            {
                "id_periodo": id_periodo,
                "id_tipo_asiento": id_tipo_asiento,
                "numero": numero,
                "fecha": fecha,
                "descripcion": descripcion,
                "estado": estado,
            },
            operacion="asiento_repository._SQL_CREAR_ASIENTO",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_asiento: int
    ) -> FilaDict | None:
        """Consulta un asiento por su identificador primario."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_asiento": id_asiento},
            operacion="asiento_repository._SQL_OBTENER_POR_ID",
        )

    async def listar_por_periodo(
        self, sesion: SesionBD, id_periodo: int
    ) -> list[FilaDict]:
        """Lista todos los asientos registrados en un periodo contable."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_PERIODO,
            {"id_periodo": id_periodo},
            operacion="asiento_repository._SQL_LISTAR_POR_PERIODO",
        )

    async def obtener_por_numero_periodo(
        self, sesion: SesionBD, *, id_periodo: int, numero: int
    ) -> FilaDict | None:
        """Busca si ya existe un asiento con el número dado dentro del periodo."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_NUMERO_PERIODO,
            {"id_periodo": id_periodo, "numero": numero},
            operacion="asiento_repository._SQL_OBTENER_POR_NUMERO_PERIODO",
        )

    async def obtener_siguiente_numero(self, sesion: SesionBD, id_periodo: int) -> int:
        """Obtiene el próximo número consecutivo para asientos del periodo."""
        fila = await ejecutar_consulta_uno(
            sesion,
            _SQL_SIGUIENTE_NUMERO_EN_PERIODO,
            {"id_periodo": id_periodo},
            operacion="asiento_repository._SQL_SIGUIENTE_NUMERO_EN_PERIODO",
        )
        if fila is None or fila.get("siguiente_numero") is None:
            return 1
        return int(fila["siguiente_numero"])

    async def actualizar_cabecera(
        self,
        sesion: SesionBD,
        *,
        id_asiento: int,
        id_tipo_asiento: int,
        fecha: date,
        descripcion: str,
    ) -> FilaDict | None:
        """Actualiza los campos editables de un asiento en borrador."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_ACTUALIZAR_CABECERA,
            {
                "id_asiento": id_asiento,
                "id_tipo_asiento": id_tipo_asiento,
                "fecha": fecha,
                "descripcion": descripcion,
            },
            operacion="asiento_repository._SQL_ACTUALIZAR_CABECERA",
        )

    async def actualizar_estado(
        self, sesion: SesionBD, *, id_asiento: int, estado: str
    ) -> FilaDict | None:
        """Actualiza el estado del asiento contable."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_ACTUALIZAR_ESTADO,
            {"id_asiento": id_asiento, "estado": estado},
            operacion="asiento_repository._SQL_ACTUALIZAR_ESTADO",
        )
