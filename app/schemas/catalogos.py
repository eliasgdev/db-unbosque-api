"""Esquemas Pydantic para los catálogos de solo lectura (RF-04, RF-08).

Incluye TIPO_CUENTA, RUBRO_ESTADO y TIPO_ASIENTO.
"""

from typing import Literal

from pydantic import BaseModel, Field

ClaseCuenta = Literal["ACTIVO", "PASIVO", "PATRIMONIO", "INGRESO", "COSTO", "GASTO"]
NaturalezaCuenta = Literal["DEBITO", "CREDITO"]
TipoEstadoFinanciero = Literal["BALANCE", "RESULTADOS"]
NombreTipoAsiento = Literal["APERTURA", "DIARIO", "AJUSTE", "CIERRE"]


class TipoCuentaOut(BaseModel):
    """Clasificación contable y naturaleza de saldo (TIPO_CUENTA)."""

    id_tipo_cuenta: int = Field(
        description="Identificador único del tipo de cuenta (PK)",
        examples=[1],
    )
    clase: ClaseCuenta = Field(
        description="Clase contable principal",
        examples=["ACTIVO"],
    )
    naturaleza: NaturalezaCuenta = Field(
        description="Naturaleza por la que aumenta el saldo de la cuenta",
        examples=["DEBITO"],
    )


class RubroEstadoOut(BaseModel):
    """Rubro jerárquico de presentación en los estados financieros (RUBRO_ESTADO)."""

    id_rubro: int = Field(
        description="Identificador único del rubro (PK)",
        examples=[10],
    )
    id_rubro_padre: int | None = Field(
        default=None,
        description="Identificador del rubro padre si es un subrubro (FK recursiva)",
        examples=[1],
    )
    codigo: str = Field(
        max_length=20,
        description="Código único del rubro en el estado financiero",
        examples=["BG-ACT-CORR"],
    )
    nombre: str = Field(
        max_length=150,
        description="Nombre de presentación del rubro",
        examples=["Activo Corriente"],
    )
    estado_financiero: TipoEstadoFinanciero = Field(
        description="Reporte al que pertenece el rubro (BALANCE o RESULTADOS)",
        examples=["BALANCE"],
    )
    orden: int = Field(
        description="Orden numérico de presentación dentro del reporte",
        examples=[1],
    )


class TipoAsientoOut(BaseModel):
    """Clasificación del asiento contable (TIPO_ASIENTO)."""

    id_tipo_asiento: int = Field(
        description="Identificador único del tipo de asiento (PK)",
        examples=[2],
    )
    nombre: NombreTipoAsiento = Field(
        description="Nombre del tipo de asiento (APERTURA, DIARIO, AJUSTE, CIERRE)",
        examples=["DIARIO"],
    )
