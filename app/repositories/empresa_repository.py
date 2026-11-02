"""Repositorio de acceso a datos para la entidad EMPRESA (RF-01)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: registrar una nueva empresa y retornar sus datos junto con el código de
#   moneda.
# Parámetros: nit (str), razon_social (str), id_moneda (int).
# Retorna: la fila insertada de EMPRESA (id_empresa, nit, razon_social, id_moneda).
# Tablas: EMPRESA.
_SQL_CREAR_EMPRESA = """"""

# Propósito: listar todas las empresas registradas con el código de su moneda base.
# Parámetros: ninguno.
# Retorna: lista de filas de EMPRESA enriquecidas con codigo_moneda.
# Tablas: EMPRESA, MONEDA.
_SQL_LISTAR_EMPRESAS = """"""

# Propósito: obtener una empresa por su identificador único.
# Parámetros: id_empresa (int).
# Retorna: una fila de EMPRESA o ninguna.
# Tablas: EMPRESA, MONEDA.
_SQL_OBTENER_POR_ID = """"""

# Propósito: buscar una empresa por su NIT para validar unicidad antes del alta.
# Parámetros: nit (str).
# Retorna: una fila de EMPRESA o ninguna.
# Tablas: EMPRESA.
_SQL_OBTENER_POR_NIT = """"""


class EmpresaRepository:
    """Operaciones de persistencia y consulta para la entidad EMPRESA."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        nit: str,
        razon_social: str,
        id_moneda: int,
    ) -> FilaDict | None:
        """Inserta una nueva empresa y retorna el registro creado."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_EMPRESA,
            {
                "nit": nit,
                "razon_social": razon_social,
                "id_moneda": id_moneda,
            },
            operacion="empresa_repository._SQL_CREAR_EMPRESA",
        )

    async def listar(self, sesion: SesionBD) -> list[FilaDict]:
        """Retorna el listado de empresas registradas."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_EMPRESAS,
            operacion="empresa_repository._SQL_LISTAR_EMPRESAS",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_empresa: int
    ) -> FilaDict | None:
        """Consulta una empresa por su identificador primario."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_empresa": id_empresa},
            operacion="empresa_repository._SQL_OBTENER_POR_ID",
        )

    async def obtener_por_nit(self, sesion: SesionBD, nit: str) -> FilaDict | None:
        """Consulta una empresa por su NIT."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_NIT,
            {"nit": nit},
            operacion="empresa_repository._SQL_OBTENER_POR_NIT",
        )
