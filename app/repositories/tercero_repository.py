"""Repositorio de acceso a datos para la entidad TERCERO (RF-10)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: registrar un nuevo tercero asociado a una empresa.
# Parámetros: id_empresa (int), documento (str), nombre (str), tipo (str).
# Retorna: la fila insertada de TERCERO.
# Tablas: TERCERO.
_SQL_CREAR_TERCERO = """"""

# Propósito: listar todos los terceros pertenecientes a una empresa ordenados por
#   nombre.
# Parámetros: id_empresa (int).
# Retorna: lista de filas de TERCERO.
# Tablas: TERCERO.
_SQL_LISTAR_POR_EMPRESA = """"""

# Propósito: obtener un tercero por su identificador único.
# Parámetros: id_tercero (int).
# Retorna: una fila de TERCERO o ninguna.
# Tablas: TERCERO.
_SQL_OBTENER_POR_ID = """"""

# Propósito: buscar un tercero por (id_empresa, documento) para validar unicidad.
# Parámetros: id_empresa (int), documento (str).
# Retorna: una fila de TERCERO o ninguna.
# Tablas: TERCERO.
_SQL_OBTENER_POR_DOCUMENTO_EMPRESA = """"""


class TerceroRepository:
    """Operaciones de persistencia y consulta para la entidad TERCERO."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        documento: str,
        nombre: str,
        tipo: str,
    ) -> FilaDict | None:
        """Inserta un nuevo tercero en la empresa indicada."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_TERCERO,
            {
                "id_empresa": id_empresa,
                "documento": documento,
                "nombre": nombre,
                "tipo": tipo,
            },
            operacion="tercero_repository._SQL_CREAR_TERCERO",
        )

    async def listar_por_empresa(
        self, sesion: SesionBD, id_empresa: int
    ) -> list[FilaDict]:
        """Lista los terceros registrados para una empresa."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_EMPRESA,
            {"id_empresa": id_empresa},
            operacion="tercero_repository._SQL_LISTAR_POR_EMPRESA",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_tercero: int
    ) -> FilaDict | None:
        """Obtiene un tercero por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_tercero": id_tercero},
            operacion="tercero_repository._SQL_OBTENER_POR_ID",
        )

    async def obtener_por_documento_empresa(
        self, sesion: SesionBD, *, id_empresa: int, documento: str
    ) -> FilaDict | None:
        """Busca un tercero por documento dentro de una empresa."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_DOCUMENTO_EMPRESA,
            {"id_empresa": id_empresa, "documento": documento},
            operacion="tercero_repository._SQL_OBTENER_POR_DOCUMENTO_EMPRESA",
        )
