"""Esquemas comunes de estado operativo y respuestas estándar de error."""

from typing import Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Estructura uniforme para las respuestas de error HTTP (404, 409, 422, 501,

    500).
    """

    codigo: str = Field(
        description="Código identificador del tipo de error de dominio",
        examples=["REGLA_DE_NEGOCIO"],
    )
    mensaje: str = Field(
        description="Descripción legible de la causa del error",
        examples=["El asiento no cumple la partida doble: suma debe != suma haber."],
    )
    detalle: str | None = Field(
        default=None,
        description="Información técnica o contextual adicional sobre el fallo",
        examples=["Suma debe: 150000.00, Suma haber: 100000.00"],
    )


class HealthResponse(BaseModel):
    """Estado de salud del servicio API y de la conectividad con PostgreSQL."""

    estado: Literal["ok", "degradado"] = Field(
        description="Estado general del servicio backend",
        examples=["ok"],
    )
    servicio: str = Field(
        description="Nombre configurado de la aplicación",
        examples=["API Sistema Contable - Universidad El Bosque"],
    )
    entorno: str = Field(
        description="Entorno de ejecución activo",
        examples=["development"],
    )
    base_datos: Literal["conectada", "sql_no_definido", "sin_conexion"] = Field(
        description="Estado reportado de la verificación contra PostgreSQL",
        examples=["sql_no_definido"],
    )
