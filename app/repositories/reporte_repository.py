"""Repositorio de consultas agregadas para Estado de Resultados, Balance General
y Cierre (RF-09, 11, 13, 14).

Considera únicamente asientos en estado CONTABILIZADO (RF-09, S-08).
"""

from datetime import date

from app.core.database import (
    FilaDict,
    SesionBD,
    ejecutar_consulta_todos,
    ejecutar_consulta_uno,
)

# Propósito: obtener los saldos acumulados por cuenta de resultado (INGRESO,
#            COSTO, GASTO) para un periodo contable sobre asientos
#            CONTABILIZADO (excluyendo asientos de tipo CIERRE).
# Parámetros: id_periodo (int).
# Retorna: lista de filas con (id_cuenta, codigo, nombre, id_rubro, clase,
#          naturaleza, total_debe, total_haber).
# Tablas: MOVIMIENTO, ASIENTO, TIPO_ASIENTO, PLAN_CUENTA, TIPO_CUENTA, RUBRO_ESTADO.
_SQL_SALDOS_RESULTADOS_POR_PERIODO = """
SELECT
    pc.id_cuenta,
    pc.codigo,
    pc.nombre,
    pc.id_rubro,
    tc.clase,
    tc.naturaleza,
    COALESCE(SUM(m.debe), 0.00) AS total_debe,
    COALESCE(SUM(m.haber), 0.00) AS total_haber
FROM movimiento m
INNER JOIN asiento a ON a.id_asiento = m.id_asiento
INNER JOIN tipo_asiento ta ON ta.id_tipo_asiento = a.id_tipo_asiento
INNER JOIN plan_cuenta pc ON pc.id_cuenta = m.id_cuenta
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
INNER JOIN rubro_estado re ON re.id_rubro = pc.id_rubro
WHERE a.id_periodo = %(id_periodo)s
  AND a.estado = 'CONTABILIZADO'
  AND ta.nombre <> 'CIERRE'
  AND tc.clase IN ('INGRESO', 'COSTO', 'GASTO')
GROUP BY
    pc.id_cuenta,
    pc.codigo,
    pc.nombre,
    pc.id_rubro,
    tc.clase,
    tc.naturaleza
ORDER BY pc.codigo ASC;
"""

# Propósito: obtener los saldos vivos de cuentas de resultado (INGRESO, COSTO,
#            GASTO) de un periodo para construir los movimientos de
#            contrapartida del asiento de CIERRE.
# Parámetros: id_periodo (int).
# Retorna: lista de filas con (id_cuenta, clase, naturaleza, total_debe, total_haber).
# Tablas: MOVIMIENTO, ASIENTO, PLAN_CUENTA, TIPO_CUENTA.
_SQL_SALDOS_PARA_CIERRE_PERIODO = """
SELECT
    pc.id_cuenta,
    tc.clase,
    tc.naturaleza,
    COALESCE(SUM(m.debe), 0.00) AS total_debe,
    COALESCE(SUM(m.haber), 0.00) AS total_haber
FROM movimiento m
INNER JOIN asiento a ON a.id_asiento = m.id_asiento
INNER JOIN plan_cuenta pc ON pc.id_cuenta = m.id_cuenta
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
WHERE a.id_periodo = %(id_periodo)s
  AND a.estado = 'CONTABILIZADO'
  AND tc.clase IN ('INGRESO', 'COSTO', 'GASTO')
GROUP BY
    pc.id_cuenta,
    tc.clase,
    tc.naturaleza
HAVING COALESCE(SUM(m.debe), 0.00) <> COALESCE(SUM(m.haber), 0.00)
ORDER BY pc.id_cuenta ASC;
"""

# Propósito: obtener los saldos acumulados de cuentas de balance (ACTIVO,
#            PASIVO, PATRIMONIO) de una empresa hasta una fecha de corte sobre
#            asientos CONTABILIZADO.
# Parámetros: id_empresa (int), fecha_corte (date).
# Retorna: lista de filas con (id_cuenta, codigo, nombre, id_rubro, clase,
#          naturaleza, total_debe, total_haber).
# Tablas: MOVIMIENTO, ASIENTO, PERIODO_CONTABLE, PLAN_CUENTA, TIPO_CUENTA,
#         RUBRO_ESTADO.
_SQL_SALDOS_BALANCE_A_CORTE = """
SELECT
    pc.id_cuenta,
    pc.codigo,
    pc.nombre,
    pc.id_rubro,
    tc.clase,
    tc.naturaleza,
    COALESCE(SUM(m.debe), 0.00) AS total_debe,
    COALESCE(SUM(m.haber), 0.00) AS total_haber
FROM movimiento m
INNER JOIN asiento a ON a.id_asiento = m.id_asiento
INNER JOIN periodo_contable p ON p.id_periodo = a.id_periodo
INNER JOIN plan_cuenta pc ON pc.id_cuenta = m.id_cuenta
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
INNER JOIN rubro_estado re ON re.id_rubro = pc.id_rubro
WHERE p.id_empresa = %(id_empresa)s
  AND a.estado = 'CONTABILIZADO'
  AND a.fecha <= %(fecha_corte)s
  AND tc.clase IN ('ACTIVO', 'PASIVO', 'PATRIMONIO')
GROUP BY
    pc.id_cuenta,
    pc.codigo,
    pc.nombre,
    pc.id_rubro,
    tc.clase,
    tc.naturaleza
HAVING COALESCE(SUM(m.debe), 0.00) <> COALESCE(SUM(m.haber), 0.00)
ORDER BY pc.codigo ASC;
"""

# Propósito: calcular los totales de ingresos, costos y gastos de asientos
#            CONTABILIZADO en periodos abiertos hasta la fecha de corte para
#            determinar la utilidad del ejercicio en curso (S-09).
# Parámetros: id_empresa (int), fecha_corte (date).
# Retorna: una fila con (total_ingresos, total_costos, total_gastos) o ninguna.
# Tablas: MOVIMIENTO, ASIENTO, PERIODO_CONTABLE, PLAN_CUENTA, TIPO_CUENTA.
_SQL_UTILIDAD_EJERCICIO_A_CORTE = """
SELECT
    COALESCE(
        SUM(
            CASE
                WHEN tc.clase = 'INGRESO' THEN (m.haber - m.debe)
                ELSE 0.00
            END
        ),
        0.00
    ) AS total_ingresos,
    COALESCE(
        SUM(
            CASE
                WHEN tc.clase = 'COSTO' THEN (m.debe - m.haber)
                ELSE 0.00
            END
        ),
        0.00
    ) AS total_costos,
    COALESCE(
        SUM(
            CASE
                WHEN tc.clase = 'GASTO' THEN (m.debe - m.haber)
                ELSE 0.00
            END
        ),
        0.00
    ) AS total_gastos
FROM movimiento m
INNER JOIN asiento a ON a.id_asiento = m.id_asiento
INNER JOIN periodo_contable p ON p.id_periodo = a.id_periodo
INNER JOIN plan_cuenta pc ON pc.id_cuenta = m.id_cuenta
INNER JOIN tipo_cuenta tc ON tc.id_tipo_cuenta = pc.id_tipo_cuenta
WHERE p.id_empresa = %(id_empresa)s
  AND a.estado = 'CONTABILIZADO'
  AND a.fecha <= %(fecha_corte)s
  AND tc.clase IN ('INGRESO', 'COSTO', 'GASTO');
"""


class ReporteRepository:
    """Consultas contables sobre movimientos contabilizados para reportes y cierre."""

    async def obtener_saldos_resultados_periodo(
        self, sesion: SesionBD, id_periodo: int
    ) -> list[FilaDict]:
        """Retorna las sumas débito y crédito de cuentas de resultado del periodo."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_SALDOS_RESULTADOS_POR_PERIODO,
            {"id_periodo": id_periodo},
            operacion="reporte_repository._SQL_SALDOS_RESULTADOS_POR_PERIODO",
        )

    async def obtener_saldos_para_cierre(
        self, sesion: SesionBD, id_periodo: int
    ) -> list[FilaDict]:
        """Retorna las sumas débito y crédito de cuentas de resultado a saldar."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_SALDOS_PARA_CIERRE_PERIODO,
            {"id_periodo": id_periodo},
            operacion="reporte_repository._SQL_SALDOS_PARA_CIERRE_PERIODO",
        )

    async def obtener_saldos_balance_a_corte(
        self, sesion: SesionBD, *, id_empresa: int, fecha_corte: date
    ) -> list[FilaDict]:
        """Retorna las sumas débito y crédito de cuentas de balance a fecha_corte."""
        return await ejecutar_consulta_todos(
            sesion,
            _SQL_SALDOS_BALANCE_A_CORTE,
            {"id_empresa": id_empresa, "fecha_corte": fecha_corte},
            operacion="reporte_repository._SQL_SALDOS_BALANCE_A_CORTE",
        )

    async def obtener_utilidad_ejercicio_a_corte(
        self, sesion: SesionBD, *, id_empresa: int, fecha_corte: date
    ) -> FilaDict | None:
        """Retorna los acumulados de resultado no cerrados a fecha_corte."""
        return await ejecutar_consulta_uno(
            sesion,
            _SQL_UTILIDAD_EJERCICIO_A_CORTE,
            {"id_empresa": id_empresa, "fecha_corte": fecha_corte},
            operacion="reporte_repository._SQL_UTILIDAD_EJERCICIO_A_CORTE",
        )
