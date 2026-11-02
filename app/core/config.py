"""Configuración central de la aplicación leída exclusivamente desde .env.

No incluye valores por defecto para credenciales ni parámetros de entorno;
si falta alguna variable en el archivo .env o en las variables de entorno,
el arranque falla con un mensaje explicativo.
"""

from functools import lru_cache
from typing import Literal

from psycopg.conninfo import make_conninfo
from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parámetros de configuración de la API y del pool de PostgreSQL."""

    app_name: str = Field(description="Título mostrado en la documentación OpenAPI")
    app_env: Literal["development", "production"] = Field(
        description="Entorno de ejecución de la aplicación"
    )
    app_host: str = Field(description="Interfaz de red donde escucha Uvicorn")
    app_port: int = Field(ge=1, le=65535, description="Puerto TCP de escucha")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        description="Nivel de registro de eventos (logging)"
    )
    cors_origins: str = Field(
        description="Orígenes permitidos para CORS, separados por coma"
    )

    db_host: str = Field(description="Host o IP del servidor PostgreSQL (VM-DB)")
    db_port: int = Field(ge=1, le=65535, description="Puerto TCP de PostgreSQL")
    db_name: str = Field(description="Nombre de la base de datos contable")
    db_user: str = Field(description="Usuario de conexión a PostgreSQL")
    db_password: str = Field(description="Contraseña del usuario de PostgreSQL")
    db_sslmode: Literal[
        "disable", "allow", "prefer", "require", "verify-ca", "verify-full"
    ] = Field(description="Modo SSL para la conexión a PostgreSQL")
    db_pool_min: int = Field(ge=1, description="Número mínimo de conexiones en el pool")
    db_pool_max: int = Field(ge=1, description="Número máximo de conexiones en el pool")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validar_rango_pool(self) -> "Settings":
        """Verifica que el tamaño máximo del pool no sea menor que el mínimo."""
        if self.db_pool_max < self.db_pool_min:
            msg = "DB_POOL_MAX debe ser mayor o igual que DB_POOL_MIN."
            raise ValueError(msg)
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna la lista limpia de orígenes CORS permitidos."""
        return [
            origen.strip() for origen in self.cors_origins.split(",") if origen.strip()
        ]

    @property
    def db_conninfo(self) -> str:
        """Construye la cadena de conexión DSN para psycopg 3.

        Usa ``make_conninfo`` para escapar los valores: una contraseña con
        espacios, comillas o barras invertidas no rompe la cadena.
        """
        return make_conninfo(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            sslmode=self.db_sslmode,
        )


@lru_cache(maxsize=1)
def obtener_settings() -> Settings:
    """Carga y cachea la configuración única desde .env.

    Lanza RuntimeError con detalle claro si faltan variables obligatorias.
    """
    try:
        return Settings()
    except ValidationError as exc:
        campos = ", ".join(
            ".".join(str(parte) for parte in err["loc"]).upper() for err in exc.errors()
        )
        mensaje = (
            "Error crítico de configuración: faltan o son inválidas las siguientes "
            f"variables en el archivo .env: [{campos}]. "
            "Verifique su archivo .env comparándolo con .env.example."
        )
        raise RuntimeError(mensaje) from exc
