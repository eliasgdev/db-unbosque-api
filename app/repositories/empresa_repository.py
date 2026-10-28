from app.core.database import fetch_all, fetch_one


def listar() -> list[dict]:
    return fetch_all("SELECT nit, registro, moneda_base FROM empresa ORDER BY registro")


def obtener(nit: str) -> dict | None:
    return fetch_one("SELECT nit, registro, moneda_base FROM empresa WHERE nit = :nit", {"nit": nit})


def periodos(nit: str) -> list[dict]:
    return fetch_all(
        """
        SELECT id, fecha_inicio, fecha_fin, estado
        FROM periodo_contable
        WHERE empresa_nit = :nit
        ORDER BY fecha_inicio
        """,
        {"nit": nit},
    )


def cuentas(nit: str) -> list[dict]:
    return fetch_all(
        """
        SELECT pc.codigo, pc.clasificacion, pc.nivel_2 AS nivel,
               tc.tipo_cuenta, tc.naturaleza_1 AS naturaleza,
               pc.plan_cuenta_codigo AS cuenta_padre
        FROM plan_cuenta pc
        JOIN tipo_cuenta tc ON tc.tipo_cuenta = pc.tipo_cuenta_tipo_cuenta
        WHERE pc.empresa_nit = :nit
        ORDER BY pc.codigo
        """,
        {"nit": nit},
    )
