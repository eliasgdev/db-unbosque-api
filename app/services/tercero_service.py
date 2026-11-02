"""Servicio de negocio para la gestión de terceros por empresa (RF-10)."""

from app.core.database import GestorBaseDatos
from app.core.exceptions import Conflicto, NoEncontrado
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.tercero_repository import TerceroRepository
from app.schemas.tercero import TerceroCreate, TerceroOut


class TerceroService:
    """Gestiona el alta y listado de terceros asociados a una empresa."""

    def __init__(
        self,
        db: GestorBaseDatos,
        tercero_repo: TerceroRepository,
        empresa_repo: EmpresaRepository,
    ) -> None:
        """Inicializa el servicio de terceros."""
        self._db = db
        self._tercero_repo = tercero_repo
        self._empresa_repo = empresa_repo

    async def crear_tercero(self, id_empresa: int, datos: TerceroCreate) -> TerceroOut:
        """Registra un nuevo tercero verificando la empresa y unicidad del documento
        (RF-10).
        """
        async with self._db.transaccion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")

            existente = await self._tercero_repo.obtener_por_documento_empresa(
                sesion, id_empresa=id_empresa, documento=datos.documento
            )
            if existente is not None:
                raise Conflicto(
                    f"Ya existe un tercero con documento '{datos.documento}' "
                    f"en la empresa id_empresa={id_empresa}."
                )

            creado = await self._tercero_repo.crear(
                sesion,
                id_empresa=id_empresa,
                documento=datos.documento,
                nombre=datos.nombre,
                tipo=datos.tipo,
            )
            if creado is None:
                raise Conflicto("No fue posible registrar el tercero.")
            return TerceroOut.model_validate(creado)

    async def listar_terceros_empresa(self, id_empresa: int) -> list[TerceroOut]:
        """Lista todos los terceros pertenecientes a una empresa (RF-10)."""
        async with self._db.conexion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")
            filas = await self._tercero_repo.listar_por_empresa(sesion, id_empresa)
        return [TerceroOut.model_validate(fila) for fila in filas]
