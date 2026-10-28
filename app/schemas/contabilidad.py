from datetime import date

from pydantic import BaseModel


class Empresa(BaseModel):
    nit: str
    registro: str
    moneda_base: float | None = None


class Periodo(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    estado: str


class Cuenta(BaseModel):
    codigo: str
    clasificacion: str
    nivel: int
    tipo_cuenta: str
    naturaleza: str
    cuenta_padre: str | None = None


class Asiento(BaseModel):
    id: int
    fecha: date
    descripcion: str
    estado: str


class Movimiento(BaseModel):
    id: int
    cuenta_codigo: str
    cuenta: str
    debe: float
    haber: float


class SaldoCuenta(BaseModel):
    codigo: str
    clasificacion: str
    tipo_cuenta: str
    saldo: float


class EstadoResultados(BaseModel):
    periodo_id: int
    ingresos: float
    costos: float
    gastos: float
    utilidad_bruta: float
    utilidad_neta: float
    cuentas: list[SaldoCuenta]


class BalanceGeneral(BaseModel):
    nit: str
    fecha_corte: date
    activo: float
    pasivo: float
    patrimonio: float
    utilidad_ejercicio: float
    cuadra: bool
    cuentas: list[SaldoCuenta]
