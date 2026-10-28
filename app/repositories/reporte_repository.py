from datetime import date

from app.core.database import fetch_all

SALDOS_QUERY = """
    SELECT pc.codigo, pc.clasificacion, tc.tipo_cuenta,
           SUM(CASE WHEN UPPER(tc.naturaleza_1) LIKE 'C%'
                    THEN m.haber - m.deber
                    ELSE m.deber - m.haber END) AS saldo
    FROM movimiento m
    JOIN asiento a ON a.id = m.asiento_id
    JOIN plan_cuenta pc ON pc.codigo = m.plan_cuenta_codigo
    JOIN tipo_cuenta tc ON tc.tipo_cuenta = pc.tipo_cuenta_tipo_cuenta
    WHERE UPPER(a.estado) = 'CONTABILIZADO' AND {filtro}
    GROUP BY pc.codigo, pc.clasificacion, tc.tipo_cuenta
    ORDER BY pc.codigo
"""


def saldos_por_periodo(periodo_id: int) -> list[dict]:
    return fetch_all(
        SALDOS_QUERY.format(filtro="a.periodo_contable_id = :periodo_id"),
        {"periodo_id": periodo_id},
    )


def saldos_a_fecha(nit: str, fecha_corte: date) -> list[dict]:
    return fetch_all(
        SALDOS_QUERY.format(filtro="a.empresa_nit = :nit AND a.fecha <= :fecha_corte"),
        {"nit": nit, "fecha_corte": fecha_corte},
    )
