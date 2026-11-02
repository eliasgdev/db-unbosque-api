"""Excepciones de dominio del Sistema Contable.

Define la jerarquía de errores de negocio e infraestructura que la capa de
servicios y repositorios lanza y que la capa API traduce a códigos HTTP.
"""


class ErrorDominio(Exception):
    """Excepción base para todos los errores de dominio del sistema contable."""

    def __init__(self, mensaje: str, detalle: str | None = None) -> None:
        """Inicializa el error de dominio con mensaje principal y detalle opcional."""
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalle = detalle


class NoEncontrado(ErrorDominio):
    """Entidad solicitada no existe en el sistema (mapeado a HTTP 404)."""


class Conflicto(ErrorDominio):
    """Conflicto con el estado actual o unicidad de datos (mapeado a HTTP 409)."""


class ReglaDeNegocio(ErrorDominio):
    """Violación de una regla contable o de validación de negocio (HTTP 422)."""


class SqlNoDefinido(ErrorDominio):
    """Sentencia SQL vacía pendiente de implementación manual (HTTP 501)."""

    def __init__(self, operacion: str) -> None:
        """Inicializa la excepción indicando qué constante o acción SQL está vacía."""
        super().__init__(
            mensaje=(
                f"La sentencia SQL para la operación '{operacion}' "
                "no ha sido definida aún."
            ),
            detalle=(
                "Las sentencias SQL se entregan vacías por diseño y deben ser "
                "escritas manualmente en la capa de repositorios."
            ),
        )
        self.operacion = operacion
