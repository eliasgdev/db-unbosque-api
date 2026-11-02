"""Esquemas Pydantic para el Estado de Resultados y el Balance General (RF-13, RF-14,
RF-15).

Todos los saldos y totales son calculados dinámicamente a partir de movimientos
en asientos CONTABILIZADO y agrupados según la jerarquía de RUBRO_ESTADO (S-07, S-11).
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaldoCuentaReporteOut(BaseModel):
    """Saldo calculado de una cuenta contable dentro de un rubro de estado

    financiero.
    """

    id_cuenta: int = Field(
        description="Identificador único de la cuenta contable",
        examples=[101],
    )
    codigo: str = Field(
        description="Código contable de la cuenta",
        examples=["110505"],
    )
    nombre: str = Field(
        description="Nombre de la cuenta contable",
        examples=["Caja General"],
    )
    clase: str = Field(
        description=(
            "Clase de cuenta (ACTIVO, PASIVO, PATRIMONIO, INGRESO, COSTO, GASTO)"
        ),
        examples=["ACTIVO"],
    )
    naturaleza: str = Field(
        description="Naturaleza del saldo de la cuenta (DEBITO o CREDITO)",
        examples=["DEBITO"],
    )
    saldo: Decimal = Field(
        description=(
            "Saldo neto calculado según la naturaleza de la cuenta (NUMERIC(20,2))"
        ),
        examples=[Decimal("45000000.00")],
    )


class RubroReporteOut(BaseModel):
    """Agrupación jerárquica de un rubro del estado financiero (RUBRO_ESTADO)."""

    id_rubro: int = Field(
        description="Identificador del rubro de estado financiero",
        examples=[10],
    )
    id_rubro_padre: int | None = Field(
        default=None,
        description="Identificador del rubro padre si es un subrubro",
        examples=[1],
    )
    codigo: str = Field(
        description="Código identificador del rubro",
        examples=["BG-ACT-CORR"],
    )
    nombre: str = Field(
        description="Nombre de presentación del rubro",
        examples=["Activo Corriente"],
    )
    orden: int = Field(
        description="Orden de aparición dentro del reporte",
        examples=[1],
    )
    subtotal: Decimal = Field(
        description="Suma de los saldos de las cuentas del rubro y de sus subrubros",
        examples=[Decimal("45000000.00")],
    )
    cuentas: list[SaldoCuentaReporteOut] = Field(
        default_factory=list,
        description="Cuentas con saldo imputadas directamente a este rubro",
    )
    subrubros: list["RubroReporteOut"] = Field(
        default_factory=list,
        description="Subrubros hijos ordenados por el atributo 'orden'",
    )


RubroReporteOut.model_rebuild()


class EstadoResultadosOut(BaseModel):
    """Estado de Resultados calculado para un periodo contable (RF-13, S-10, S-11)."""

    id_periodo: int = Field(
        description="Identificador del periodo contable consultado",
        examples=[1],
    )
    id_empresa: int = Field(
        description="Identificador de la empresa",
        examples=[1],
    )
    fecha_inicio: date = Field(
        description="Fecha de inicio del periodo evaluado",
        examples=["2026-01-01"],
    )
    fecha_fin: date = Field(
        description="Fecha de fin del periodo evaluado",
        examples=["2026-12-31"],
    )
    ingresos: Decimal = Field(
        description="Total de ingresos acumulados en asientos CONTABILIZADO",
        examples=[Decimal("120000000.00")],
    )
    costos: Decimal = Field(
        description="Total de costos de venta/producción acumulados",
        examples=[Decimal("50000000.00")],
    )
    gastos: Decimal = Field(
        description="Total de gastos operacionales y no operacionales acumulados",
        examples=[Decimal("44600000.00")],
    )
    utilidad_bruta: Decimal = Field(
        description="Utilidad Bruta calculada (Ingresos - Costos)",
        examples=[Decimal("70000000.00")],
    )
    utilidad_operacional: Decimal = Field(
        description="Utilidad Operacional calculada según rubros operacionales",
        examples=[Decimal("30000000.00")],
    )
    utilidad_neta: Decimal = Field(
        description=(
            "Utilidad o pérdida neta del ejercicio (Ingresos - Costos - Gastos)"
        ),
        examples=[Decimal("25400000.00")],
    )
    rubros: list[RubroReporteOut] = Field(
        default_factory=list,
        description=(
            "Árbol de rubros del Estado de Resultados definido por RUBRO_ESTADO"
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_periodo": 1,
                    "id_empresa": 1,
                    "fecha_inicio": "2026-01-01",
                    "fecha_fin": "2026-12-31",
                    "ingresos": "120000000.00",
                    "costos": "50000000.00",
                    "gastos": "44600000.00",
                    "utilidad_bruta": "70000000.00",
                    "utilidad_operacional": "30000000.00",
                    "utilidad_neta": "25400000.00",
                    "rubros": [
                        {
                            "id_rubro": 20,
                            "id_rubro_padre": None,
                            "codigo": "ER-ING-OPER",
                            "nombre": "Ingresos Operacionales",
                            "orden": 1,
                            "subtotal": "120000000.00",
                            "cuentas": [
                                {
                                    "id_cuenta": 401,
                                    "codigo": "413505",
                                    "nombre": "Comercio al por mayor y al por menor",
                                    "clase": "INGRESO",
                                    "naturaleza": "CREDITO",
                                    "saldo": "120000000.00",
                                }
                            ],
                            "subrubros": [],
                        }
                    ],
                }
            ]
        }
    )


class BalanceGeneralOut(BaseModel):
    """Balance General clasificado a una fecha de corte (RF-14, S-09, S-11)."""

    id_empresa: int = Field(
        description="Identificador de la empresa consultada",
        examples=[1],
    )
    razon_social: str = Field(
        description="Razón social de la empresa",
        examples=["Comercializadora El Bosque S.A.S."],
    )
    fecha_corte: date = Field(
        description=(
            "Fecha de corte hasta la cual se acumulan los saldos contabilizados"
        ),
        examples=["2026-12-31"],
    )
    total_activo: Decimal = Field(
        description="Suma total de los saldos de las cuentas de ACTIVO",
        examples=[Decimal("85400000.00")],
    )
    total_pasivo: Decimal = Field(
        description="Suma total de los saldos de las cuentas de PASIVO",
        examples=[Decimal("20000000.00")],
    )
    total_patrimonio: Decimal = Field(
        description=(
            "Suma de las cuentas de PATRIMONIO más la utilidad del ejercicio en curso"
        ),
        examples=[Decimal("65400000.00")],
    )
    utilidad_ejercicio: Decimal = Field(
        description=(
            "Utilidad o pérdida acumulada de periodos aún abiertos hasta la fecha de "
            "corte (S-09)"
        ),
        examples=[Decimal("25400000.00")],
    )
    diferencia_ecuacion: Decimal = Field(
        description="Diferencia absoluta Activo - (Pasivo + Patrimonio); debe ser 0.00",
        examples=[Decimal("0.00")],
    )
    cuadra: bool = Field(
        description=(
            "Indica si se cumple la ecuación patrimonial Activo = Pasivo + Patrimonio"
        ),
        examples=[True],
    )
    rubros: list[RubroReporteOut] = Field(
        default_factory=list,
        description="Árbol de rubros del Balance General definido por RUBRO_ESTADO",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_empresa": 1,
                    "razon_social": "Comercializadora El Bosque S.A.S.",
                    "fecha_corte": "2026-12-31",
                    "total_activo": "85400000.00",
                    "total_pasivo": "20000000.00",
                    "total_patrimonio": "65400000.00",
                    "utilidad_ejercicio": "25400000.00",
                    "diferencia_ecuacion": "0.00",
                    "cuadra": True,
                    "rubros": [
                        {
                            "id_rubro": 1,
                            "id_rubro_padre": None,
                            "codigo": "BG-ACT",
                            "nombre": "Activo",
                            "orden": 1,
                            "subtotal": "85400000.00",
                            "cuentas": [],
                            "subrubros": [
                                {
                                    "id_rubro": 10,
                                    "id_rubro_padre": 1,
                                    "codigo": "BG-ACT-CORR",
                                    "nombre": "Activo Corriente",
                                    "orden": 1,
                                    "subtotal": "85400000.00",
                                    "cuentas": [
                                        {
                                            "id_cuenta": 101,
                                            "codigo": "110505",
                                            "nombre": "Caja General",
                                            "clase": "ACTIVO",
                                            "naturaleza": "DEBITO",
                                            "saldo": "85400000.00",
                                        }
                                    ],
                                    "subrubros": [],
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    )
