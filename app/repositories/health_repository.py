"""Repositorio para la verificación de conectividad con PostgreSQL."""

from app.core.database import FilaDict, SesionBD, ejecutar_consulta_uno

# Propósito: verificar que la conexión con PostgreSQL responde correctamente.
# Parámetros: ninguno.
# Retorna: una fila con un indicador de verificación o ninguna.
# Tablas: ninguna (catálogo del motor PostgreSQL).
_SQL_VERIFICAR_CONEXION = """
SELECT 1 AS ok;
"""


class HealthRepository:
    """Acceso a datos para comprobación de salud de la base de datos."""

    async def verificar_conexion(self, sesion: SesionBD) -> FilaDict | None:
        """Ejecuta la consulta de diagnóstico de conectividad."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_VERIFICAR_CONEXION,
            operacion="health_repository._SQL_VERIFICAR_CONEXION",
        )
