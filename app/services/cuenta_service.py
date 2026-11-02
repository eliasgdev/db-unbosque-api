"""Servicio de negocio para el Plan de Cuentas jerárquico (RF-03, RF-04, RF-05,

RF-15).
"""

from app.core.database import GestorBaseDatos
from app.core.exceptions import Conflicto, NoEncontrado, ReglaDeNegocio
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.rubro_estado_repository import RubroEstadoRepository
from app.repositories.tipo_cuenta_repository import TipoCuentaRepository
from app.schemas.cuenta import CuentaArbolOut, CuentaCreate, CuentaOut


class CuentaService:
    """Gestiona el alta de cuentas contables y la construcción del árbol jerárquico."""

    def __init__(
        self,
        db: GestorBaseDatos,
        cuenta_repo: CuentaRepository,
        empresa_repo: EmpresaRepository,
        tipo_cuenta_repo: TipoCuentaRepository,
        rubro_repo: RubroEstadoRepository,
    ) -> None:
        """Inicializa el servicio de cuentas contables."""
        self._db = db
        self._cuenta_repo = cuenta_repo
        self._empresa_repo = empresa_repo
        self._tipo_cuenta_repo = tipo_cuenta_repo
        self._rubro_repo = rubro_repo

    async def crear_cuenta(self, id_empresa: int, datos: CuentaCreate) -> CuentaOut:
        """Registra una cuenta en el plan de la empresa validando su jerarquía (RF-03,
        04,
        05).
        """
        async with self._db.transaccion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")

            tipo_cuenta = await self._tipo_cuenta_repo.obtener_por_id(
                sesion, datos.id_tipo_cuenta
            )
            if tipo_cuenta is None:
                raise NoEncontrado(
                    f"El tipo de cuenta con id_tipo_cuenta={datos.id_tipo_cuenta} no "
                    "existe."
                )

            rubro = await self._rubro_repo.obtener_por_id(sesion, datos.id_rubro)
            if rubro is None:
                raise NoEncontrado(
                    f"El rubro de estado con id_rubro={datos.id_rubro} no existe."
                )

            duplicada = await self._cuenta_repo.obtener_por_codigo_empresa(
                sesion, id_empresa=id_empresa, codigo=datos.codigo
            )
            if duplicada is not None:
                raise Conflicto(
                    f"Ya existe una cuenta con código '{datos.codigo}' en la empresa "
                    f"id_empresa={id_empresa}."
                )

            if datos.id_cuenta_padre is not None:
                padre = await self._cuenta_repo.obtener_por_id(
                    sesion, datos.id_cuenta_padre
                )
                if padre is None:
                    raise NoEncontrado(
                        f"La cuenta padre con id_cuenta={datos.id_cuenta_padre} no "
                        "existe."
                    )
                if int(padre["id_empresa"]) != id_empresa:
                    raise ReglaDeNegocio(
                        "La cuenta padre debe pertenecer a la misma empresa (S-06)."
                    )
                if bool(padre.get("acepta_movimiento")):
                    raise ReglaDeNegocio(
                        "Una cuenta marcada con acepta_movimiento=true (hoja) no "
                        "puede tener subcuentas hijas."
                    )
                nivel_padre = int(padre["nivel"])
                if datos.nivel <= nivel_padre:
                    raise ReglaDeNegocio(
                        f"El nivel de la cuenta hija ({datos.nivel}) debe ser mayor "
                        f"que el de su cuenta padre ({nivel_padre})."
                    )

            creada = await self._cuenta_repo.crear(
                sesion,
                id_empresa=id_empresa,
                id_cuenta_padre=datos.id_cuenta_padre,
                id_tipo_cuenta=datos.id_tipo_cuenta,
                id_rubro=datos.id_rubro,
                codigo=datos.codigo,
                nombre=datos.nombre,
                nivel=datos.nivel,
                acepta_movimiento=datos.acepta_movimiento,
            )
            if creada is None:
                raise Conflicto("No fue posible registrar la cuenta contable.")

            creada.setdefault("clase_cuenta", tipo_cuenta.get("clase"))
            creada.setdefault("naturaleza", tipo_cuenta.get("naturaleza"))
            return CuentaOut.model_validate(creada)

    async def listar_plan_cuentas(self, id_empresa: int) -> list[CuentaArbolOut]:
        """Obtiene el plan de cuentas de una empresa estructurado como árbol recursivo
        (RF-03, RF-15).
        """
        async with self._db.conexion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")
            filas = await self._cuenta_repo.listar_por_empresa(sesion, id_empresa)

        nodos_por_id: dict[int, CuentaArbolOut] = {}
        raices: list[CuentaArbolOut] = []

        for fila in filas:
            nodo = CuentaArbolOut.model_validate({**fila, "subcuentas": []})
            nodos_por_id[nodo.id_cuenta] = nodo

        for nodo in nodos_por_id.values():
            if (
                nodo.id_cuenta_padre is not None
                and nodo.id_cuenta_padre in nodos_por_id
            ):
                nodos_por_id[nodo.id_cuenta_padre].subcuentas.append(nodo)
            else:
                raices.append(nodo)

        return raices

    async def obtener_cuenta(self, id_cuenta: int) -> CuentaOut:
        """Consulta el detalle de una cuenta contable por su identificador (RF-03)."""
        async with self._db.conexion() as sesion:
            fila = await self._cuenta_repo.obtener_por_id(sesion, id_cuenta)
        if fila is None:
            raise NoEncontrado(f"La cuenta con id_cuenta={id_cuenta} no existe.")
        return CuentaOut.model_validate(fila)
