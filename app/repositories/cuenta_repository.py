"""Repositorio de acceso a datos para PLAN_CUENTA (RF-03, RF-04, RF-05, RF-15)."""

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: registrar una nueva cuenta dentro del plan de cuentas de una empresa.
# Parámetros: id_empresa (int), id_cuenta_padre (int | None),
#             id_tipo_cuenta (int), id_rubro (int), codigo (str), nombre (str),
#             nivel (int), acepta_movimiento (bool).
# Retorna: la fila insertada de PLAN_CUENTA.
# Tablas: PLAN_CUENTA.
_SQL_CREAR_CUENTA = """
INSERT INTO plan_cuenta (
    id_empresa,
    id_cuenta_padre,
    id_tipo_cuenta,
    id_rubro,
    codigo,
    nombre,
    nivel,
    acepta_movimiento
)
VALUES (
    %(id_empresa)s,
    %(id_cuenta_padre)s,
    %(id_tipo_cuenta)s,
    %(id_rubro)s,
    %(codigo)s,
    %(nombre)s,
    %(nivel)s,
    %(acepta_movimiento)s
)
RETURNING
    id_cuenta,
    id_empresa,
    id_cuenta_padre,
    id_tipo_cuenta,
    id_rubro,
    codigo,
    nombre,
    nivel,
    acepta_movimiento;
"""

# Propósito: listar todas las cuentas del plan de una empresa ordenadas por
#            código junto con su clase, naturaleza y cuenta padre opcional
#            (LEFT JOIN porque las cuentas raíz de nivel 1 no tienen padre).
# Parámetros: id_empresa (int).
# Retorna: lista de filas de PLAN_CUENTA enriquecidas con clase_cuenta y naturaleza.
# Tablas: PLAN_CUENTA, TIPO_CUENTA, RUBRO_ESTADO.
_SQL_LISTAR_POR_EMPRESA = """
SELECT
    pc.id_cuenta,
    pc.id_empresa,
    pc.id_cuenta_padre,
    pc.id_tipo_cuenta,
    pc.id_rubro,
    pc.codigo,
    pc.nombre,
    pc.nivel,
    pc.acepta_movimiento,
    tc.clase AS clase_cuenta,
    tc.naturaleza
FROM plan_cuenta pc
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
INNER JOIN rubro_estado re ON re.id_rubro = pc.id_rubro
LEFT JOIN plan_cuenta padre ON padre.id_cuenta = pc.id_cuenta_padre
WHERE pc.id_empresa = %(id_empresa)s
ORDER BY pc.nivel ASC, pc.codigo ASC;
"""

# Propósito: obtener una cuenta contable por su identificador único junto con
#            su clase, naturaleza y relación opcional a cuenta padre (LEFT JOIN).
# Parámetros: id_cuenta (int).
# Retorna: una fila de PLAN_CUENTA o ninguna.
# Tablas: PLAN_CUENTA, TIPO_CUENTA, RUBRO_ESTADO.
_SQL_OBTENER_POR_ID = """
SELECT
    pc.id_cuenta,
    pc.id_empresa,
    pc.id_cuenta_padre,
    pc.id_tipo_cuenta,
    pc.id_rubro,
    pc.codigo,
    pc.nombre,
    pc.nivel,
    pc.acepta_movimiento,
    tc.clase AS clase_cuenta,
    tc.naturaleza
FROM plan_cuenta pc
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
INNER JOIN rubro_estado re ON re.id_rubro = pc.id_rubro
LEFT JOIN plan_cuenta padre ON padre.id_cuenta = pc.id_cuenta_padre
WHERE pc.id_cuenta = %(id_cuenta)s;
"""

# Propósito: buscar una cuenta por el par único (id_empresa, codigo) para
#            verificar duplicados.
# Parámetros: id_empresa (int), codigo (str).
# Retorna: una fila de PLAN_CUENTA o ninguna.
# Tablas: PLAN_CUENTA.
_SQL_OBTENER_POR_CODIGO_EMPRESA = """
SELECT
    id_cuenta,
    id_empresa,
    id_cuenta_padre,
    id_tipo_cuenta,
    id_rubro,
    codigo,
    nombre,
    nivel,
    acepta_movimiento
FROM plan_cuenta
WHERE id_empresa = %(id_empresa)s
  AND codigo = %(codigo)s;
"""


class CuentaRepository:
    """Operaciones de persistencia y consulta sobre PLAN_CUENTA."""

    async def crear(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        id_cuenta_padre: int | None,
        id_tipo_cuenta: int,
        id_rubro: int,
        codigo: str,
        nombre: str,
        nivel: int,
        acepta_movimiento: bool,
    ) -> FilaDict | None:
        """Inserta una cuenta en el plan contable de la empresa."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_CREAR_CUENTA,
            {
                "id_empresa": id_empresa,
                "id_cuenta_padre": id_cuenta_padre,
                "id_tipo_cuenta": id_tipo_cuenta,
                "id_rubro": id_rubro,
                "codigo": codigo,
                "nombre": nombre,
                "nivel": nivel,
                "acepta_movimiento": acepta_movimiento,
            },
            operacion="cuenta_repository._SQL_CREAR_CUENTA",
        )

    async def listar_por_empresa(
        self, sesion: SesionBD, id_empresa: int
    ) -> list[FilaDict]:
        """Retorna todas las cuentas del plan de una empresa."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_LISTAR_POR_EMPRESA,
            {"id_empresa": id_empresa},
            operacion="cuenta_repository._SQL_LISTAR_POR_EMPRESA",
        )

    async def obtener_por_id(self, sesion: SesionBD, id_cuenta: int) -> FilaDict | None:
        """Obtiene una cuenta por su clave primaria."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_ID,
            {"id_cuenta": id_cuenta},
            operacion="cuenta_repository._SQL_OBTENER_POR_ID",
        )

    async def obtener_por_codigo_empresa(
        self, sesion: SesionBD, *, id_empresa: int, codigo: str
    ) -> FilaDict | None:
        """Busca una cuenta por código dentro de la misma empresa."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_OBTENER_POR_CODIGO_EMPRESA,
            {"id_empresa": id_empresa, "codigo": codigo},
            operacion="cuenta_repository._SQL_OBTENER_POR_CODIGO_EMPRESA",
        )
