"""Esquemas Pydantic para la entidad EMPRESA (RF-01)."""

from pydantic import BaseModel, Field


class EmpresaCreate(BaseModel):
    """Datos de entrada para registrar una nueva empresa."""

    nit: str = Field(
        min_length=5,
        max_length=20,
        description="Número de Identificación Tributaria único de la empresa",
        examples=["900123456-7"],
    )
    razon_social: str = Field(
        min_length=2,
        max_length=200,
        description="Nombre o razón social legal de la empresa",
        examples=["Comercializadora El Bosque S.A.S."],
    )
    id_moneda: int = Field(
        gt=0,
        description="Identificador de la moneda funcional base (FK -> MONEDA)",
        examples=[1],
    )


class EmpresaOut(BaseModel):
    """Datos de salida de una empresa registrada."""

    id_empresa: int = Field(
        description="Identificador único de la empresa (PK)",
        examples=[1],
    )
    nit: str = Field(
        description="Número de Identificación Tributaria único de la empresa",
        examples=["900123456-7"],
    )
    razon_social: str = Field(
        description="Razón social legal de la empresa",
        examples=["Comercializadora El Bosque S.A.S."],
    )
    id_moneda: int = Field(
        description="Identificador de la moneda base (FK -> MONEDA)",
        examples=[1],
    )
    codigo_moneda: str | None = Field(
        default=None,
        description="Código ISO de la moneda base (cuando se enriquece en consulta)",
        examples=["COP"],
    )
