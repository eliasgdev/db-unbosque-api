"""Esquemas Pydantic para el Plan de Cuentas jerárquico (PLAN_CUENTA, RF-03, 04, 05,

15).
"""

from pydantic import BaseModel, Field


class CuentaCreate(BaseModel):
    """Datos de entrada para registrar una nueva cuenta en el plan de una empresa."""

    id_cuenta_padre: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Identificador de la cuenta padre en la jerarquía (NULL si es raíz)"
        ),
        examples=[1],
    )
    id_tipo_cuenta: int = Field(
        gt=0,
        description="Identificador del tipo de cuenta (FK -> TIPO_CUENTA)",
        examples=[1],
    )
    id_rubro: int = Field(
        gt=0,
        description="Identificador del rubro de estado financiero (FK -> RUBRO_ESTADO)",
        examples=[10],
    )
    codigo: str = Field(
        min_length=1,
        max_length=20,
        description="Código contable único dentro de la empresa (ej. 110505)",
        examples=["110505"],
    )
    nombre: str = Field(
        min_length=2,
        max_length=150,
        description="Nombre descriptivo de la cuenta contable",
        examples=["Caja General"],
    )
    nivel: int = Field(
        ge=1,
        le=10,
        description=(
            "Nivel jerárquico de la cuenta (1=Clase, 2=Grupo, 3=Cuenta, 4=Subcuenta)"
        ),
        examples=[4],
    )
    acepta_movimiento: bool = Field(
        description=(
            "Indica si la cuenta es hoja y permite imputar movimientos contables"
        ),
        examples=[True],
    )


class CuentaOut(BaseModel):
    """Representación plana de una cuenta del plan contable."""

    id_cuenta: int = Field(
        description="Identificador único de la cuenta (PK)",
        examples=[101],
    )
    id_empresa: int = Field(
        description="Identificador de la empresa propietaria (FK -> EMPRESA)",
        examples=[1],
    )
    id_cuenta_padre: int | None = Field(
        default=None,
        description="Identificador de la cuenta padre (FK recursiva -> PLAN_CUENTA)",
        examples=[100],
    )
    id_tipo_cuenta: int = Field(
        description="Identificador del tipo de cuenta (FK -> TIPO_CUENTA)",
        examples=[1],
    )
    id_rubro: int = Field(
        description="Identificador del rubro de estado financiero (FK -> RUBRO_ESTADO)",
        examples=[10],
    )
    codigo: str = Field(
        description="Código contable dentro del plan de la empresa",
        examples=["110505"],
    )
    nombre: str = Field(
        description="Nombre de la cuenta contable",
        examples=["Caja General"],
    )
    nivel: int = Field(
        description="Nivel dentro del árbol del plan de cuentas",
        examples=[4],
    )
    acepta_movimiento: bool = Field(
        description="True si permite asientos directos (cuenta hoja)",
        examples=[True],
    )
    clase_cuenta: str | None = Field(
        default=None,
        description="Clase contable heredada de TIPO_CUENTA (ACTIVO, PASIVO, etc.)",
        examples=["ACTIVO"],
    )
    naturaleza: str | None = Field(
        default=None,
        description="Naturaleza del saldo (DEBITO o CREDITO)",
        examples=["DEBITO"],
    )


class CuentaArbolOut(CuentaOut):
    """Nodo recursivo del plan de cuentas jerárquico de una empresa."""

    subcuentas: list["CuentaArbolOut"] = Field(
        default_factory=list,
        description="Lista de cuentas hijas directas ordenadas por código",
    )


CuentaArbolOut.model_rebuild()
