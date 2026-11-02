"""Esquemas Pydantic para la entidad TERCERO (RF-10)."""

from typing import Literal

from pydantic import BaseModel, Field

TipoTercero = Literal["CLIENTE", "PROVEEDOR", "OTRO"]


class TerceroCreate(BaseModel):
    """Datos de entrada para registrar un tercero en una empresa."""

    documento: str = Field(
        min_length=3,
        max_length=20,
        description="Número de documento o NIT del tercero (único por empresa)",
        examples=["800987654-3"],
    )
    nombre: str = Field(
        min_length=2,
        max_length=200,
        description="Nombre completo o razón social del tercero",
        examples=["Distribuidora Los Andes S.A."],
    )
    tipo: TipoTercero = Field(
        description="Clasificación del tercero (CLIENTE, PROVEEDOR u OTRO)",
        examples=["PROVEEDOR"],
    )


class TerceroOut(BaseModel):
    """Representación de un tercero registrado."""

    id_tercero: int = Field(
        description="Identificador único del tercero (PK)",
        examples=[1],
    )
    id_empresa: int = Field(
        description="Identificador de la empresa a la que pertenece (FK -> EMPRESA)",
        examples=[1],
    )
    documento: str = Field(
        description="Documento de identificación del tercero",
        examples=["800987654-3"],
    )
    nombre: str = Field(
        description="Nombre o razón social del tercero",
        examples=["Distribuidora Los Andes S.A."],
    )
    tipo: TipoTercero = Field(
        description="Rol del tercero respecto a la empresa",
        examples=["PROVEEDOR"],
    )
