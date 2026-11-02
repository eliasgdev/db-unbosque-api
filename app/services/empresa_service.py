"""Servicio de negocio para la gestión de empresas (RF-01)."""

from app.core.database import GestorBaseDatos
from app.core.exceptions import Conflicto, NoEncontrado
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.moneda_repository import MonedaRepository
from app.schemas.empresa import EmpresaCreate, EmpresaOut


class EmpresaService:
    """Gestiona el registro y consulta de empresas y su moneda funcional."""

    def __init__(
        self,
        db: GestorBaseDatos,
        empresa_repo: EmpresaRepository,
        moneda_repo: MonedaRepository,
    ) -> None:
        """Inicializa el servicio de empresas."""
        self._db = db
        self._empresa_repo = empresa_repo
        self._moneda_repo = moneda_repo

    async def crear_empresa(self, datos: EmpresaCreate) -> EmpresaOut:
        """Registra una nueva empresa validando moneda base y unicidad del NIT

        (RF-01).
        """
        async with self._db.transaccion() as sesion:
            moneda = await self._moneda_repo.obtener_por_id(sesion, datos.id_moneda)
            if moneda is None:
                raise NoEncontrado(
                    f"La moneda con id_moneda={datos.id_moneda} no existe."
                )

            existente = await self._empresa_repo.obtener_por_nit(sesion, datos.nit)
            if existente is not None:
                raise Conflicto(
                    f"Ya existe una empresa registrada con el NIT '{datos.nit}'."
                )

            creada = await self._empresa_repo.crear(
                sesion,
                nit=datos.nit,
                razon_social=datos.razon_social,
                id_moneda=datos.id_moneda,
            )
            if creada is None:
                raise Conflicto("No fue posible registrar la empresa.")

            creada.setdefault("codigo_moneda", moneda.get("codigo"))
            return EmpresaOut.model_validate(creada)

    async def listar_empresas(self) -> list[EmpresaOut]:
        """Lista todas las empresas registradas (RF-01)."""
        async with self._db.conexion() as sesion:
            filas = await self._empresa_repo.listar(sesion)
        return [EmpresaOut.model_validate(fila) for fila in filas]

    async def obtener_empresa(self, id_empresa: int) -> EmpresaOut:
        """Consulta una empresa por su identificador primario (RF-01)."""
        async with self._db.conexion() as sesion:
            fila = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
        if fila is None:
            raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")
        return EmpresaOut.model_validate(fila)
