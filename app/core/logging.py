"""Configuración centralizada de logging de la aplicación.

Prohíbe el uso de print() y estandariza el formato de salida hacia stdout.
"""

import logging
import sys


def configurar_logging(nivel: str) -> None:
    """Configura el logger raíz de la aplicación con el nivel indicado en .env."""
    nivel_numerico = getattr(logging, nivel.upper(), logging.INFO)
    formato = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.basicConfig(
        level=nivel_numerico,
        format=formato,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve una instancia de logger con el nombre del módulo."""
    return logging.getLogger(nombre)
