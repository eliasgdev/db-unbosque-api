"""Servicio de negocio para la gestión de centros de costo por empresa (RF-10)."""

from app.core.database import GestorBaseDatos
from app.core.exceptions import Conflicto, NoEncontrado
from app.repositories.centro_costo_repository import CentroCostoRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.centro_costo import CentroCostoCreate, CentroCostoOut


class CentroCostoService:
    """Gestiona el alta y consulta de centros de costo por empresa."""

    def __init__(
        self,
        db: GestorBaseDatos,
        centro_costo_repo: CentroCostoRepository,
        empresa_repo: EmpresaRepository,
    ) -> None:
        """Inicializa el servicio de centros de costo."""
        self._db = db
        self._centro_costo_repo = centro_costo_repo
        self._empresa_repo = empresa_repo

    async def crear_centro_costo(
        self, id_empresa: int, datos: CentroCostoCreate
    ) -> CentroCostoOut:
        """Registra un centro de costo validando empresa y unicidad del código

        (RF-10).
        """
        async with self._db.transaccion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")

            existente = await self._centro_costo_repo.obtener_por_codigo_empresa(
                sesion, id_empresa=id_empresa, codigo=datos.codigo
            )
            if existente is not None:
                raise Conflicto(
                    f"Ya existe un centro de costo con código '{datos.codigo}' "
                    f"en la empresa id_empresa={id_empresa}."
                )

            creado = await self._centro_costo_repo.crear(
                sesion,
                id_empresa=id_empresa,
                codigo=datos.codigo,
                nombre=datos.nombre,
            )
            if creado is None:
                raise Conflicto("No fue posible registrar el centro de costo.")
            return CentroCostoOut.model_validate(creado)

    async def listar_centros_costo_empresa(
        self, id_empresa: int
    ) -> list[CentroCostoOut]:
        """Lista todos los centros de costo registrados para una empresa (RF-10)."""
        async with self._db.conexion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")
            filas = await self._centro_costo_repo.listar_por_empresa(sesion, id_empresa)
        return [CentroCostoOut.model_validate(fila) for fila in filas]
