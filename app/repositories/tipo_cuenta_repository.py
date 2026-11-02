"""Repositorio de acceso a datos para el catálogo TIPO_CUENTA (RF-04)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: listar todos los tipos de cuenta del catálogo (clase y naturaleza).
# Parámetros: ninguno.
# Retorna: lista de filas de TIPO_CUENTA.
# Tablas: TIPO_CUENTA.
_SQL_LISTAR_TIPOS_CUENTA = """"""

# Propósito: obtener un tipo de cuenta por su identificador primario.
# Parámetros: id_tipo_cuenta (int).
# Retorna: una fila de TIPO_CUENTA o ninguna.
# Tablas: TIPO_CUENTA.
_SQL_OBTENER_POR_ID = """"""


class TipoCuentaRepository:
    """Operaciones de solo lectura sobre el catálogo TIPO_CUENTA."""

    async def listar(self, sesion: SesionBD) -> list[FilaDict]:
        """Lista todos los tipos de cuenta disponibles."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_TIPOS_CUENTA,
            operacion="tipo_cuenta_repository._SQL_LISTAR_TIPOS_CUENTA",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_tipo_cuenta: int
    ) -> FilaDict | None:
        """Obtiene un tipo de cuenta por su identificador."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_tipo_cuenta": id_tipo_cuenta},
            operacion="tipo_cuenta_repository._SQL_OBTENER_POR_ID",
        )
