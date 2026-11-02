"""Repositorio de acceso a datos para la entidad MONEDA (RF-01)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: listar todas las monedas registradas en el catálogo ordenadas por código.
# Parámetros: ninguno.
# Retorna: lista de filas de MONEDA (id_moneda, codigo, nombre, simbolo).
# Tablas: MONEDA.
_SQL_LISTAR_MONEDAS = """
SELECT
    id_moneda,
    codigo,
    nombre,
    simbolo
FROM moneda
ORDER BY codigo ASC;
"""

# Propósito: obtener una moneda por su identificador primario.
# Parámetros: id_moneda (int).
# Retorna: una fila de MONEDA o ninguna.
# Tablas: MONEDA.
_SQL_OBTENER_POR_ID = """
SELECT
    id_moneda,
    codigo,
    nombre,
    simbolo
FROM moneda
WHERE id_moneda = %(id_moneda)s;
"""


class MonedaRepository:
    """Operaciones de consulta sobre la tabla MONEDA."""

    async def listar(self, sesion: SesionBD) -> list[FilaDict]:
        """Retorna todas las monedas disponibles en el catálogo."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_MONEDAS,
            operacion="moneda_repository._SQL_LISTAR_MONEDAS",
        )

    async def obtener_por_id(self, sesion: SesionBD, id_moneda: int) -> FilaDict | None:
        """Busca una moneda específica por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_moneda": id_moneda},
            operacion="moneda_repository._SQL_OBTENER_POR_ID",
        )
