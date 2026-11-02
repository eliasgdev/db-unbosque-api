"""Repositorio de acceso a datos para el catálogo RUBRO_ESTADO (RF-04, S-11)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: listar todos los rubros de estados financieros ordenados por
#            estado_financiero y orden, incluyendo LEFT JOIN a su rubro padre.
# Parámetros: ninguno.
# Retorna: lista de filas de RUBRO_ESTADO.
# Tablas: RUBRO_ESTADO.
_SQL_LISTAR_RUBROS = """
SELECT
    r.id_rubro,
    r.id_rubro_padre,
    r.codigo,
    r.nombre,
    r.estado_financiero,
    r.orden
FROM rubro_estado r
LEFT JOIN rubro_estado rp ON rp.id_rubro = r.id_rubro_padre
ORDER BY r.estado_financiero ASC, r.orden ASC, r.id_rubro ASC;
"""

# Propósito: listar los rubros pertenecientes a un estado financiero específico
#            (BALANCE o RESULTADOS) usando LEFT JOIN sobre el rubro padre.
# Parámetros: estado_financiero (str).
# Retorna: lista de filas de RUBRO_ESTADO ordenadas por orden.
# Tablas: RUBRO_ESTADO.
_SQL_LISTAR_POR_ESTADO_FINANCIERO = """
SELECT
    r.id_rubro,
    r.id_rubro_padre,
    r.codigo,
    r.nombre,
    r.estado_financiero,
    r.orden
FROM rubro_estado r
LEFT JOIN rubro_estado rp ON rp.id_rubro = r.id_rubro_padre
WHERE r.estado_financiero = %(estado_financiero)s
ORDER BY r.orden ASC, r.id_rubro ASC;
"""

# Propósito: obtener un rubro de estado financiero por su identificador primario.
# Parámetros: id_rubro (int).
# Retorna: una fila de RUBRO_ESTADO o ninguna.
# Tablas: RUBRO_ESTADO.
_SQL_OBTENER_POR_ID = """
SELECT
    r.id_rubro,
    r.id_rubro_padre,
    r.codigo,
    r.nombre,
    r.estado_financiero,
    r.orden
FROM rubro_estado r
LEFT JOIN rubro_estado rp ON rp.id_rubro = r.id_rubro_padre
WHERE r.id_rubro = %(id_rubro)s;
"""


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
