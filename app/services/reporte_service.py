import unicodedata
from datetime import date

from app.repositories import reporte_repository

CLASES = ("activo", "pasivo", "patrimonio", "ingreso", "costo", "gasto")


def _clase(tipo_cuenta: str) -> str | None:
    texto = unicodedata.normalize("NFKD", tipo_cuenta).encode("ascii", "ignore").decode().lower()
    return next((c for c in CLASES if texto.startswith(c)), None)


def _totales(cuentas: list[dict]) -> dict:
    totales = dict.fromkeys(CLASES, 0)
    for cuenta in cuentas:
        clase = _clase(cuenta["tipo_cuenta"])
        if clase:
            totales[clase] += cuenta["saldo"]
    return totales


def estado_resultados(periodo_id: int) -> dict:
    cuentas = reporte_repository.saldos_por_periodo(periodo_id)
    t = _totales(cuentas)
    utilidad_bruta = t["ingreso"] - t["costo"]
    return {
        "periodo_id": periodo_id,
        "ingresos": t["ingreso"],
        "costos": t["costo"],
        "gastos": t["gasto"],
        "utilidad_bruta": utilidad_bruta,
        "utilidad_neta": utilidad_bruta - t["gasto"],
        "cuentas": [c for c in cuentas if _clase(c["tipo_cuenta"]) in ("ingreso", "costo", "gasto")],
    }


def balance_general(nit: str, fecha_corte: date) -> dict:
    cuentas = reporte_repository.saldos_a_fecha(nit, fecha_corte)
    t = _totales(cuentas)
    utilidad = t["ingreso"] - t["costo"] - t["gasto"]
    return {
        "nit": nit,
        "fecha_corte": fecha_corte,
        "activo": t["activo"],
        "pasivo": t["pasivo"],
        "patrimonio": t["patrimonio"],
        "utilidad_ejercicio": utilidad,
        "cuadra": round(t["activo"] - t["pasivo"] - t["patrimonio"] - utilidad, 2) == 0,
        "cuentas": [c for c in cuentas if _clase(c["tipo_cuenta"]) in ("activo", "pasivo", "patrimonio")],
    }
