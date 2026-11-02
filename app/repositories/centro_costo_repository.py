"""Repositorio de acceso a datos para la entidad CENTRO_COSTO (RF-10)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: registrar un nuevo centro de costo asociado a una empresa.
# Parámetros: id_empresa (int), codigo (str), nombre (str).
# Retorna: la fila insertada de CENTRO_COSTO.
# Tablas: CENTRO_COSTO.
_SQL_CREAR_CENTRO_COSTO = """"""

# Propósito: listar todos los centros de costo de una empresa ordenados por código.
# Parámetros: id_empresa (int).
# Retorna: lista de filas de CENTRO_COSTO.
# Tablas: CENTRO_COSTO.
_SQL_LISTAR_POR_EMPRESA = """"""

# Propósito: obtener un centro de costo por su identificador único.
# Parámetros: id_centro_costo (int).
# Retorna: una fila de CENTRO_COSTO o ninguna.
# Tablas: CENTRO_COSTO.
_SQL_OBTENER_POR_ID = """"""

# Propósito: buscar un centro de costo por (id_empresa, codigo) para validar unicidad.
# Parámetros: id_empresa (int), codigo (str).
# Retorna: una fila de CENTRO_COSTO o ninguna.
# Tablas: CENTRO_COSTO.
_SQL_OBTENER_POR_CODIGO_EMPRESA = """"""


class CentroCostoRepository:
    """Operaciones de persistencia y consulta para CENTRO_COSTO."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        codigo: str,
        nombre: str,
    ) -> FilaDict | None:
        """Inserta un nuevo centro de costo en la empresa."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_CENTRO_COSTO,
            {
                "id_empresa": id_empresa,
                "codigo": codigo,
                "nombre": nombre,
            },
            operacion="centro_costo_repository._SQL_CREAR_CENTRO_COSTO",
        )

    async def listar_por_empresa(
        self, sesion: SesionBD, id_empresa: int
    ) -> list[FilaDict]:
        """Lista los centros de costo de una empresa."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_EMPRESA,
            {"id_empresa": id_empresa},
            operacion="centro_costo_repository._SQL_LISTAR_POR_EMPRESA",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_centro_costo: int
    ) -> FilaDict | None:
        """Obtiene un centro de costo por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_centro_costo": id_centro_costo},
            operacion="centro_costo_repository._SQL_OBTENER_POR_ID",
        )

    async def obtener_por_codigo_empresa(
        self, sesion: SesionBD, *, id_empresa: int, codigo: str
    ) -> FilaDict | None:
        """Busca un centro de costo por código dentro de una empresa."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_CODIGO_EMPRESA,
            {"id_empresa": id_empresa, "codigo": codigo},
            operacion="centro_costo_repository._SQL_OBTENER_POR_CODIGO_EMPRESA",
        )
