"""Repositorio de acceso a datos para el catálogo TIPO_ASIENTO (RF-08)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: listar todos los tipos de asiento contable (APERTURA, DIARIO, AJUSTE,
#   CIERRE).
# Parámetros: ninguno.
# Retorna: lista de filas de TIPO_ASIENTO.
# Tablas: TIPO_ASIENTO.
_SQL_LISTAR_TIPOS_ASIENTO = """"""

# Propósito: obtener un tipo de asiento por su identificador primario.
# Parámetros: id_tipo_asiento (int).
# Retorna: una fila de TIPO_ASIENTO o ninguna.
# Tablas: TIPO_ASIENTO.
_SQL_OBTENER_POR_ID = """"""

# Propósito: obtener un tipo de asiento por su nombre único (ej. CIERRE).
# Parámetros: nombre (str).
# Retorna: una fila de TIPO_ASIENTO o ninguna.
# Tablas: TIPO_ASIENTO.
_SQL_OBTENER_POR_NOMBRE = """"""


class TipoAsientoRepository:
    """Operaciones de solo lectura sobre el catálogo TIPO_ASIENTO."""

    async def listar(self, sesion: SesionBD) -> list[FilaDict]:
        """Lista los tipos de asiento disponibles en el sistema."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_TIPOS_ASIENTO,
            operacion="tipo_asiento_repository._SQL_LISTAR_TIPOS_ASIENTO",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_tipo_asiento: int
    ) -> FilaDict | None:
        """Obtiene un tipo de asiento por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_tipo_asiento": id_tipo_asiento},
            operacion="tipo_asiento_repository._SQL_OBTENER_POR_ID",
        )

    async def obtener_por_nombre(
        self, sesion: SesionBD, nombre: str
    ) -> FilaDict | None:
        """Obtiene un tipo de asiento por su nombre exacto."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_NOMBRE,
            {"nombre": nombre},
            operacion="tipo_asiento_repository._SQL_OBTENER_POR_NOMBRE",
        )
