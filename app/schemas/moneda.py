"""Esquemas Pydantic para la entidad MONEDA (RF-01)."""

from pydantic import BaseModel, Field


class MonedaOut(BaseModel):
    """Representación de una moneda del catálogo del sistema."""

    id_moneda: int = Field(
        description="Identificador único de la moneda (PK)",
        examples=[1],
    )
    codigo: str = Field(
        min_length=3,
        max_length=3,
        description="Código ISO 4217 de 3 caracteres",
        examples=["COP"],
    )
    nombre: str = Field(
        max_length=60,
        description="Nombre oficial de la moneda",
        examples=["Peso Colombiano"],
    )
    simbolo: str = Field(
        max_length=5,
        description="Símbolo monetario de presentación",
        examples=["$"],
    )
