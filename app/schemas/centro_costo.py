"""Esquemas Pydantic para la entidad CENTRO_COSTO (RF-10)."""

from pydantic import BaseModel, Field


class CentroCostoCreate(BaseModel):
    """Datos de entrada para registrar un centro de costo en una empresa."""

    codigo: str = Field(
        min_length=1,
        max_length=20,
        description="Código único del centro de costo dentro de la empresa",
        examples=["CC-ADM-01"],
    )
    nombre: str = Field(
        min_length=2,
        max_length=150,
        description="Nombre descriptivo del centro de costo",
        examples=["Administración Central"],
    )


class CentroCostoOut(BaseModel):
    """Representación de un centro de costo registrado."""

    id_centro_costo: int = Field(
        description="Identificador único del centro de costo (PK)",
        examples=[1],
    )
    id_empresa: int = Field(
        description="Identificador de la empresa propietaria (FK -> EMPRESA)",
        examples=[1],
    )
    codigo: str = Field(
        description="Código del centro de costo",
        examples=["CC-ADM-01"],
    )
    nombre: str = Field(
        description="Nombre del centro de costo",
        examples=["Administración Central"],
    )
