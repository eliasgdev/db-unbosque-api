"""Repositorio de acceso a datos para el catálogo RUBRO_ESTADO (RF-04, S-11)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: listar todos los rubros de estados financieros ordenados por
#   estado_financiero y orden.
# Parámetros: ninguno.
# Retorna: lista de filas de RUBRO_ESTADO.
# Tablas: RUBRO_ESTADO.
_SQL_LISTAR_RUBROS = """"""

# Propósito: listar los rubros pertenecientes a un estado financiero específico (BALANCE
#   o RESULTADOS).
# Parámetros: estado_financiero (str).
# Retorna: lista de filas de RUBRO_ESTADO ordenadas por orden.
# Tablas: RUBRO_ESTADO.
_SQL_LISTAR_POR_ESTADO_FINANCIERO = """"""

# Propósito: obtener un rubro de estado financiero por su identificador primario.
# Parámetros: id_rubro (int).
# Retorna: una fila de RUBRO_ESTADO o ninguna.
# Tablas: RUBRO_ESTADO.
_SQL_OBTENER_POR_ID = """"""


class RubroEstadoRepository:
    """Operaciones de consulta sobre la tabla RUBRO_ESTADO."""

    async def listar(self, sesion: SesionBD) -> list[FilaDict]:
        """Lista la totalidad de rubros configurados."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_RUBROS,
            operacion="rubro_estado_repository._SQL_LISTAR_RUBROS",
        )

    async def listar_por_estado_financiero(
        self, sesion: SesionBD, estado_financiero: str
    ) -> list[FilaDict]:
        """Lista los rubros filtrados por tipo de reporte (BALANCE o RESULTADOS)."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_ESTADO_FINANCIERO,
            {"estado_financiero": estado_financiero},
            operacion="rubro_estado_repository._SQL_LISTAR_POR_ESTADO_FINANCIERO",
        )

    async def obtener_por_id(self, sesion: SesionBD, id_rubro: int) -> FilaDict | None:
        """Obtiene un rubro por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_rubro": id_rubro},
            operacion="rubro_estado_repository._SQL_OBTENER_POR_ID",
        )
