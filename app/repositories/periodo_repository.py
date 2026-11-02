"""Repositorio de acceso a datos para PERIODO_CONTABLE (RF-02, RF-11, RF-12)."""

from datetime import date

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: crear un nuevo periodo contable en estado ABIERTO para una empresa.
# Parámetros: id_empresa (int), fecha_inicio (date), fecha_fin (date), estado (str).
# Retorna: la fila insertada de PERIODO_CONTABLE.
# Tablas: PERIODO_CONTABLE.
_SQL_CREAR_PERIODO = """
INSERT INTO periodo_contable (id_empresa, fecha_inicio, fecha_fin, estado)
VALUES (%(id_empresa)s, %(fecha_inicio)s, %(fecha_fin)s, %(estado)s)
RETURNING id_periodo, id_empresa, fecha_inicio, fecha_fin, estado;
"""

# Propósito: listar los periodos contables de una empresa ordenados por fecha_inicio.
# Parámetros: id_empresa (int).
# Retorna: lista de filas de PERIODO_CONTABLE.
# Tablas: PERIODO_CONTABLE.
_SQL_LISTAR_POR_EMPRESA = """
SELECT
    id_periodo,
    id_empresa,
    fecha_inicio,
    fecha_fin,
    estado
FROM periodo_contable
WHERE id_empresa = %(id_empresa)s
ORDER BY fecha_inicio ASC;
"""

# Propósito: obtener un periodo contable por su identificador único.
# Parámetros: id_periodo (int).
# Retorna: una fila de PERIODO_CONTABLE o ninguna.
# Tablas: PERIODO_CONTABLE.
_SQL_OBTENER_POR_ID = """
SELECT
    id_periodo,
    id_empresa,
    fecha_inicio,
    fecha_fin,
    estado
FROM periodo_contable
WHERE id_periodo = %(id_periodo)s;
"""

# Propósito: verificar si existe algún periodo de la misma empresa que se traslape.
# Parámetros: id_empresa (int), fecha_inicio (date), fecha_fin (date).
# Retorna: una fila del periodo traslapado si existe, o ninguna.
# Tablas: PERIODO_CONTABLE.
_SQL_BUSCAR_TRASLAPE = """
SELECT
    id_periodo,
    id_empresa,
    fecha_inicio,
    fecha_fin,
    estado
FROM periodo_contable
WHERE id_empresa = %(id_empresa)s
  AND fecha_inicio <= %(fecha_fin)s
  AND fecha_fin >= %(fecha_inicio)s
LIMIT 1;
"""

# Propósito: actualizar el estado de un periodo contable (ej. pasar a CERRADO).
# Parámetros: id_periodo (int), estado (str).
# Retorna: la fila actualizada de PERIODO_CONTABLE.
# Tablas: PERIODO_CONTABLE.
_SQL_ACTUALIZAR_ESTADO = """
UPDATE periodo_contable
SET estado = %(estado)s
WHERE id_periodo = %(id_periodo)s
RETURNING id_periodo, id_empresa, fecha_inicio, fecha_fin, estado;
"""


class PeriodoRepository:
    """Operaciones de persistencia y consulta para PERIODO_CONTABLE."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        fecha_inicio: date,
        fecha_fin: date,
        estado: str = "ABIERTO",
    ) -> FilaDict | None:
        """Inserta un nuevo periodo contable para la empresa indicada."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_PERIODO,
            {
                "id_empresa": id_empresa,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "estado": estado,
            },
            operacion="periodo_repository._SQL_CREAR_PERIODO",
        )

    async def listar_por_empresa(
        self, sesion: SesionBD, id_empresa: int
    ) -> list[FilaDict]:
        """Lista todos los periodos contables pertenecientes a una empresa."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_EMPRESA,
            {"id_empresa": id_empresa},
            operacion="periodo_repository._SQL_LISTAR_POR_EMPRESA",
        )

    async def obtener_por_id(
        self, sesion: SesionBD, id_periodo: int
    ) -> FilaDict | None:
        """Obtiene un periodo contable por su identificador primario."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_periodo": id_periodo},
            operacion="periodo_repository._SQL_OBTENER_POR_ID",
        )

    async def buscar_traslape(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> FilaDict | None:
        """Busca si otro periodo de la empresa se solapa con el rango dado."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_BUSCAR_TRASLAPE,
            {
                "id_empresa": id_empresa,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
            },
            operacion="periodo_repository._SQL_BUSCAR_TRASLAPE",
        )

    async def actualizar_estado(
        self,
        sesion: SesionBD,
        *,
        id_periodo: int,
        estado: str,
    ) -> FilaDict | None:
        """Actualiza el estado del periodo contable y retorna la fila actualizada."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_ACTUALIZAR_ESTADO,
            {"id_periodo": id_periodo, "estado": estado},
            operacion="periodo_repository._SQL_ACTUALIZAR_ESTADO",
        )
