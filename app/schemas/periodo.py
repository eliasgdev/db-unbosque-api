"""Esquemas Pydantic para PERIODO_CONTABLE y CIERRE_PERIODO (RF-02, RF-11, RF-12)."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

EstadoPeriodo = Literal["ABIERTO", "CERRADO"]


class PeriodoCreate(BaseModel):
    """Datos de entrada para abrir un nuevo periodo contable en una empresa."""

    fecha_inicio: date = Field(
        description="Fecha de inicio del periodo contable (inclusive)",
        examples=["2026-01-01"],
    )
    fecha_fin: date = Field(
        description="Fecha de finalización del periodo contable (inclusive)",
        examples=["2026-12-31"],
    )

    @model_validator(mode="after")
    def validar_rango_fechas(self) -> "PeriodoCreate":
        """Verifica que la fecha de fin sea estrictamente posterior a la de inicio."""
        if self.fecha_fin <= self.fecha_inicio:
            msg = "La fecha_fin debe ser estrictamente mayor que fecha_inicio."
            raise ValueError(msg)
        return self


class PeriodoOut(BaseModel):
    """Representación de un periodo contable registrado."""

    id_periodo: int = Field(
        description="Identificador único del periodo contable (PK)",
        examples=[1],
    )
    id_empresa: int = Field(
        description="Identificador de la empresa propietaria (FK -> EMPRESA)",
        examples=[1],
    )
    fecha_inicio: date = Field(
        description="Fecha de inicio del periodo contable",
        examples=["2026-01-01"],
    )
    fecha_fin: date = Field(
        description="Fecha de fin del periodo contable",
        examples=["2026-12-31"],
    )
    estado: EstadoPeriodo = Field(
        description="Estado actual del periodo (ABIERTO o CERRADO)",
        examples=["ABIERTO"],
    )


class CierrePeriodoCreate(BaseModel):
    """Parámetros requeridos para ejecutar el cierre contable de un periodo."""

    id_cuenta_patrimonio: int = Field(
        gt=0,
        description=(
            "Identificador de la cuenta hoja de PATRIMONIO donde se trasladará "
            "la utilidad o pérdida del ejercicio al generar el asiento de cierre"
        ),
        examples=[360505],
    )
    descripcion_asiento: str = Field(
        default="Cierre contable del ejercicio y traslado de utilidad al patrimonio",
        min_length=5,
        max_length=300,
        description="Descripción para el asiento automático de tipo CIERRE",
        examples=["Cierre contable del ejercicio 2026 y traslado de utilidad neta"],
    )


class CierrePeriodoOut(BaseModel):
    """Información resultante del cierre de un periodo contable (CIERRE_PERIODO)."""

    id_cierre: int = Field(
        description="Identificador único del registro de cierre (PK)",
        examples=[1],
    )
    id_periodo: int = Field(
        description="Identificador del periodo cerrado (FK 1:1 -> PERIODO_CONTABLE)",
        examples=[1],
    )
    id_asiento_cierre: int | None = Field(
        default=None,
        description="Identificador del asiento de tipo CIERRE generado (FK -> ASIENTO)",
        examples=[42],
    )
    utilidad_neta: Decimal = Field(
        description="Utilidad (positiva) o pérdida (negativa) trasladada al patrimonio",
        examples=[Decimal("25400000.00")],
    )
    fecha_cierre: datetime = Field(
        description="Marca de tiempo con zona horaria en que se ejecutó el cierre",
        examples=["2026-12-31T23:59:00-05:00"],
    )
