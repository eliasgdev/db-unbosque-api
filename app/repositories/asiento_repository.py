from app.core.database import fetch_all


def por_periodo(periodo_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT id, fecha, descripcion, estado
        FROM asiento
        WHERE periodo_contable_id = :periodo_id
        ORDER BY fecha, id
        """,
        {"periodo_id": periodo_id},
    )


def movimientos(asiento_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT m.id, pc.codigo AS cuenta_codigo, pc.clasificacion AS cuenta,
               m.deber AS debe, m.haber
        FROM movimiento m
        JOIN plan_cuenta pc ON pc.codigo = m.plan_cuenta_codigo
        WHERE m.asiento_id = :asiento_id
        ORDER BY m.id
        """,
        {"asiento_id": asiento_id},
    )
