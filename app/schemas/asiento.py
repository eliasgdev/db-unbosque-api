"""Esquemas Pydantic para ASIENTO y MOVIMIENTO (RF-06, RF-07, RF-08, RF-09, RF-12,

RF-15).
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EstadoAsiento = Literal["BORRADOR", "CONTABILIZADO"]
CERO = Decimal("0.00")


class MovimientoCreate(BaseModel):
    """Renglón de movimiento débito o crédito a registrar en un asiento."""

    id_cuenta: int = Field(
        gt=0,
        description="Identificador de la cuenta contable hoja (FK -> PLAN_CUENTA)",
        examples=[101],
    )
    id_tercero: int | None = Field(
        default=None,
        gt=0,
        description="Identificador opcional del tercero asociado (FK -> TERCERO)",
        examples=[1],
    )
    id_centro_costo: int | None = Field(
        default=None,
        gt=0,
        description="Identificador opcional del centro de costo (FK -> CENTRO_COSTO)",
        examples=[1],
    )
    debe: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=20,
        decimal_places=2,
        description="Valor débito del movimiento (NUMERIC(20,2)); excluyente con haber",
        examples=[Decimal("1500000.00")],
    )
    haber: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=20,
        decimal_places=2,
        description="Valor crédito del movimiento (NUMERIC(20,2)); excluyente con debe",
        examples=[Decimal("0.00")],
    )

    @model_validator(mode="after")
    def validar_debe_o_haber_exclusivo(self) -> "MovimientoCreate":
        """Aplica S-21: exactamente uno entre debe y haber debe ser mayor que cero."""
        debe_positivo = self.debe > CERO
        haber_positivo = self.haber > CERO
        if debe_positivo == haber_positivo:
            msg = (
                "Cada movimiento debe tener exactamente un valor mayor que cero "
                "en 'debe' o en 'haber', pero no en ambos ni ambos en cero (S-21)."
            )
            raise ValueError(msg)
        return self


class MovimientoOut(BaseModel):
    """Renglón de movimiento contable almacenado en un asiento."""

    id_movimiento: int = Field(
        description="Identificador único del movimiento (PK)",
        examples=[1],
    )
    id_asiento: int = Field(
        description="Identificador del asiento padre (FK -> ASIENTO)",
        examples=[10],
    )
    id_cuenta: int = Field(
        description="Identificador de la cuenta imputada (FK -> PLAN_CUENTA)",
        examples=[101],
    )
    codigo_cuenta: str | None = Field(
        default=None,
        description="Código contable de la cuenta imputada",
        examples=["110505"],
    )
    nombre_cuenta: str | None = Field(
        default=None,
        description="Nombre de la cuenta imputada",
        examples=["Caja General"],
    )
    id_tercero: int | None = Field(
        default=None,
        description="Identificador del tercero asociado si aplica",
        examples=[1],
    )
    id_centro_costo: int | None = Field(
        default=None,
        description="Identificador del centro de costo asociado si aplica",
        examples=[1],
    )
    debe: Decimal = Field(
        description="Monto débito registrado (NUMERIC(20,2))",
        examples=[Decimal("1500000.00")],
    )
    haber: Decimal = Field(
        description="Monto crédito registrado (NUMERIC(20,2))",
        examples=[Decimal("0.00")],
    )


class AsientoCreate(BaseModel):
    """Solicitud para registrar un nuevo asiento contable en estado BORRADOR."""

    id_tipo_asiento: int = Field(
        gt=0,
        description="Identificador del tipo de asiento (FK -> TIPO_ASIENTO)",
        examples=[2],
    )
    numero: int = Field(
        gt=0,
        description="Número consecutivo del asiento dentro del periodo",
        examples=[1],
    )
    fecha: date = Field(
        description="Fecha contable del asiento (debe estar dentro del periodo)",
        examples=["2026-03-15"],
    )
    descripcion: str = Field(
        min_length=3,
        max_length=300,
        description="Concepto o glosa explicativa del asiento contable",
        examples=["Venta de mercancía al contado según factura FV-001"],
    )
    movimientos: list[MovimientoCreate] = Field(
        min_length=1,
        description="Lista de movimientos débito y crédito del asiento",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_tipo_asiento": 2,
                    "numero": 1,
                    "fecha": "2026-03-15",
                    "descripcion": "Venta de mercancía al contado según factura FV-001",
                    "movimientos": [
                        {
                            "id_cuenta": 101,
                            "id_tercero": 1,
                            "id_centro_costo": 1,
                            "debe": "1500000.00",
                            "haber": "0.00",
                        },
                        {
                            "id_cuenta": 401,
                            "id_tercero": 1,
                            "id_centro_costo": 1,
                            "debe": "0.00",
                            "haber": "1500000.00",
                        },
                    ],
                }
            ]
        }
    )


class AsientoUpdate(BaseModel):
    """Solicitud para modificar un asiento en estado BORRADOR de un periodo ABIERTO."""

    id_tipo_asiento: int = Field(
        gt=0,
        description="Identificador del tipo de asiento (FK -> TIPO_ASIENTO)",
        examples=[2],
    )
    fecha: date = Field(
        description="Nueva fecha contable dentro del rango del periodo",
        examples=["2026-03-16"],
    )
    descripcion: str = Field(
        min_length=3,
        max_length=300,
        description="Concepto actualizado del asiento contable",
        examples=["Venta de mercancía ajustada según factura FV-001"],
    )
    movimientos: list[MovimientoCreate] = Field(
        min_length=1,
        description=(
            "Lista actualizada de movimientos que reemplaza el detalle en borrador"
        ),
    )


class AsientoResumenOut(BaseModel):
    """Vista resumida de la cabecera de un asiento contable para listados."""

    id_asiento: int = Field(
        description="Identificador único del asiento (PK)",
        examples=[10],
    )
    id_periodo: int = Field(
        description="Identificador del periodo contable (FK -> PERIODO_CONTABLE)",
        examples=[1],
    )
    id_tipo_asiento: int = Field(
        description="Identificador del tipo de asiento (FK -> TIPO_ASIENTO)",
        examples=[2],
    )
    tipo_asiento: str | None = Field(
        default=None,
        description="Nombre del tipo de asiento (APERTURA, DIARIO, AJUSTE, CIERRE)",
        examples=["DIARIO"],
    )
    numero: int = Field(
        description="Número del asiento dentro del periodo",
        examples=[1],
    )
    fecha: date = Field(
        description="Fecha contable del asiento",
        examples=["2026-03-15"],
    )
    descripcion: str = Field(
        description="Glosa o descripción del asiento",
        examples=["Venta de mercancía al contado según factura FV-001"],
    )
    estado: EstadoAsiento = Field(
        description="Estado del asiento (BORRADOR o CONTABILIZADO)",
        examples=["CONTABILIZADO"],
    )
    total_debe: Decimal = Field(
        default=Decimal("0.00"),
        description="Suma calculada de los débitos del asiento",
        examples=[Decimal("1500000.00")],
    )
    total_haber: Decimal = Field(
        default=Decimal("0.00"),
        description="Suma calculada de los créditos del asiento",
        examples=[Decimal("1500000.00")],
    )


class AsientoDetalleOut(AsientoResumenOut):
    """Detalle completo de un asiento contable junto con sus movimientos."""

    cuadra: bool = Field(
        description="Indica si la suma de débitos es igual a la suma de créditos",
        examples=[True],
    )
    movimientos: list[MovimientoOut] = Field(
        default_factory=list,
        description="Renglones de movimiento débito/crédito del asiento",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_asiento": 10,
                    "id_periodo": 1,
                    "id_tipo_asiento": 2,
                    "tipo_asiento": "DIARIO",
                    "numero": 1,
                    "fecha": "2026-03-15",
                    "descripcion": "Venta de mercancía al contado según factura FV-001",
                    "estado": "CONTABILIZADO",
                    "total_debe": "1500000.00",
                    "total_haber": "1500000.00",
                    "cuadra": True,
                    "movimientos": [
                        {
                            "id_movimiento": 1,
                            "id_asiento": 10,
                            "id_cuenta": 101,
                            "codigo_cuenta": "110505",
                            "nombre_cuenta": "Caja General",
                            "id_tercero": 1,
                            "id_centro_costo": 1,
                            "debe": "1500000.00",
                            "haber": "0.00",
                        },
                        {
                            "id_movimiento": 2,
                            "id_asiento": 10,
                            "id_cuenta": 401,
                            "codigo_cuenta": "413505",
                            "nombre_cuenta": "Comercio al por mayor y al por menor",
                            "id_tercero": 1,
                            "id_centro_costo": 1,
                            "debe": "0.00",
                            "haber": "1500000.00",
                        },
                    ],
                }
            ]
        }
    )
