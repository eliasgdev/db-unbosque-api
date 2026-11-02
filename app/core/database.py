"""Gestión del pool asíncrono de PostgreSQL, transacciones y ejecución SQL.

Implementa el acceso a datos con psycopg 3 y psycopg_pool sin ORM.
Garantiza que ninguna sentencia SQL vacía llegue al motor de base de datos,
lanzando SqlNoDefinido (HTTP 501) cuando la constante SQL está en blanco.
"""

from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from typing import Any

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.core.config import Settings
from app.core.exceptions import SqlNoDefinido
from app.core.logging import obtener_logger

logger = obtener_logger(__name__)

FilaDict = dict[str, Any]
ConexionAsync = AsyncConnection[FilaDict]
ParametrosSQL = Sequence[Any] | Mapping[str, Any] | None


class _ConexionDiferida:
    """Representa una conexión lógica diferida hasta que exista SQL definido.

    Permite que las rutas y servicios ejecuten la guardia de SqlNoDefinido (501)
    incluso en entornos de desarrollo donde PostgreSQL aún no esté en ejecución,
    y abre la conexión real del pool cuando una sentencia SQL tiene contenido.
    """

    def __init__(
        self,
        pool: AsyncConnectionPool[ConexionAsync],
        transaccional: bool,
    ) -> None:
        """Inicializa el contenedor de conexión diferida."""
        self._pool = pool
        self._transaccional = transaccional
        self._conn_ctx: Any = None
        self._tx_ctx: Any = None
        self._conn: ConexionAsync | None = None

    async def obtener_conexion_real(self) -> ConexionAsync:
        """Adquiere la conexión física (y transacción si aplica) bajo demanda."""
        if self._conn is None:
            self._conn_ctx = self._pool.connection()
            self._conn = await self._conn_ctx.__aenter__()
            if self._transaccional:
                self._tx_ctx = self._conn.transaction()
                await self._tx_ctx.__aenter__()
        return self._conn

    async def cerrar(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Cierra la transacción y devuelve la conexión al pool si fue abierta."""
        try:
            if self._tx_ctx is not None:
                await self._tx_ctx.__aexit__(exc_type, exc_val, exc_tb)
        finally:
            if self._conn_ctx is not None:
                await self._conn_ctx.__aexit__(exc_type, exc_val, exc_tb)


SesionBD = ConexionAsync | _ConexionDiferida


class GestorBaseDatos:
    """Administra el ciclo de vida del AsyncConnectionPool de PostgreSQL."""

    def __init__(self, settings: Settings) -> None:
        """Configura el pool asíncrono sin abrir conexiones inmediatamente."""
        self._settings = settings
        self._pool: AsyncConnectionPool[ConexionAsync] | None = None

    async def iniciar_pool(self) -> None:
        """Inicializa la instancia del pool asíncrono durante el lifespan."""
        self._pool = AsyncConnectionPool(
            conninfo=self._settings.db_conninfo,
            min_size=self._settings.db_pool_min,
            max_size=self._settings.db_pool_max,
            open=False,
            kwargs={"row_factory": dict_row},
        )
        logger.info(
            "Pool asíncrono de PostgreSQL configurado (min=%s, max=%s, host=%s:%s/%s)",
            self._settings.db_pool_min,
            self._settings.db_pool_max,
            self._settings.db_host,
            self._settings.db_port,
            self._settings.db_name,
        )

    async def cerrar_pool(self) -> None:
        """Cierra ordenadamente las conexiones activas del pool al apagar la app."""
        if self._pool is not None:
            await self._pool.close()
            logger.info("Pool asíncrono de PostgreSQL cerrado correctamente.")

    async def _asegurar_pool_abierto(
        self,
    ) -> AsyncConnectionPool[ConexionAsync]:
        """Garantiza que el pool esté instanciado y abierto antes de conectar."""
        if self._pool is None:
            await self.iniciar_pool()
        assert self._pool is not None
        if self._pool.closed:
            await self._pool.open(wait=False)
        return self._pool

    @asynccontextmanager
    async def conexion(self) -> AsyncIterator[SesionBD]:
        """Provee una sesión de lectura hacia PostgreSQL."""
        pool = await self._asegurar_pool_abierto()
        sesion = _ConexionDiferida(pool=pool, transaccional=False)
        try:
            yield sesion
        except BaseException as exc:
            await sesion.cerrar(type(exc), exc, exc.__traceback__)
            raise
        else:
            await sesion.cerrar(None, None, None)

    @asynccontextmanager
    async def transaccion(self) -> AsyncIterator[SesionBD]:
        """Provee una sesión transaccional atómica (COMMIT / ROLLBACK automático)."""
        pool = await self._asegurar_pool_abierto()
        sesion = _ConexionDiferida(pool=pool, transaccional=True)
        try:
            yield sesion
        except BaseException as exc:
            await sesion.cerrar(type(exc), exc, exc.__traceback__)
            raise
        else:
            await sesion.cerrar(None, None, None)


def validar_sql_definido(sql: str, operacion: str) -> str:
    """Verifica que la sentencia SQL no esté vacía antes de enviarla a la BD.

    Lanza SqlNoDefinido (HTTP 501) si la constante contiene una cadena vacía
    o únicamente espacios en blanco.
    """
    sentencia = sql.strip()
    if not sentencia:
        raise SqlNoDefinido(operacion=operacion)
    return sentencia


async def _resolver_conexion(sesion: SesionBD) -> ConexionAsync:
    """Obtiene la conexión real de psycopg a partir de una sesión."""
    if isinstance(sesion, _ConexionDiferida):
        return await sesion.obtener_conexion_real()
    return sesion


async def ejecutar_consulta_uno(
    sesion: SesionBD,
    sql: str,
    params: ParametrosSQL = None,
    *,
    operacion: str,
) -> FilaDict | None:
    """Ejecuta una sentencia SQL parametrizada y retorna una única fila o None."""
    sentencia = validar_sql_definido(sql, operacion)
    conn = await _resolver_conexion(sesion)
    async with conn.cursor() as cur:
        await cur.execute(sentencia, params)
        return await cur.fetchone()


async def ejecutar_consulta_todos(
    sesion: SesionBD,
    sql: str,
    params: ParametrosSQL = None,
    *,
    operacion: str,
) -> list[FilaDict]:
    """Ejecuta una sentencia SQL parametrizada y retorna todas las filas."""
    sentencia = validar_sql_definido(sql, operacion)
    conn = await _resolver_conexion(sesion)
    async with conn.cursor() as cur:
        await cur.execute(sentencia, params)
        filas = await cur.fetchall()
        return list(filas)


async def ejecutar_comando(
    sesion: SesionBD,
    sql: str,
    params: ParametrosSQL = None,
    *,
    operacion: str,
) -> int:
    """Ejecuta una sentencia DML parametrizada sin retorno de filas."""
    sentencia = validar_sql_definido(sql, operacion)
    conn = await _resolver_conexion(sesion)
    async with conn.cursor() as cur:
        await cur.execute(sentencia, params)
        return cur.rowcount
