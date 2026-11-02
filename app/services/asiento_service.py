"""Servicio de negocio para asientos y movimientos contables (RF-05, 06, 07, 08, 09, 10,
12, 15).

Aplica las reglas contables de la Sección 12 del User Brief:
- Bloqueo de creación y modificación en periodos CERRADO (RF-12, S-15).
- Fecha del asiento dentro del rango [fecha_inicio, fecha_fin] del periodo (S-14).
- Movimientos solo sobre cuentas con acepta_movimiento = true (RF-05, S-05).
- Cuenta, tercero y centro de costo pertenecientes a la misma empresa del periodo
  (S-06, S-18).
- Partida doble estricta (suma debe == suma haber > 0) al contabilizar (RF-07, S-01).
"""

from datetime import date
from decimal import Decimal

from app.core.database import FilaDict, GestorBaseDatos, SesionBD
from app.core.exceptions import Conflicto, NoEncontrado, ReglaDeNegocio
from app.repositories.asiento_repository import AsientoRepository
from app.repositories.centro_costo_repository import CentroCostoRepository
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.tercero_repository import TerceroRepository
from app.repositories.tipo_asiento_repository import TipoAsientoRepository
from app.schemas.asiento import (
    AsientoCreate,
    AsientoDetalleOut,
    AsientoResumenOut,
    AsientoUpdate,
    MovimientoCreate,
    MovimientoOut,
)

CERO = Decimal("0.00")


class AsientoService:
    """Gestiona el ciclo de vida de los asientos contables y sus movimientos."""

    def __init__(
        self,
        db: GestorBaseDatos,
        asiento_repo: AsientoRepository,
        movimiento_repo: MovimientoRepository,
        periodo_repo: PeriodoRepository,
        tipo_asiento_repo: TipoAsientoRepository,
        cuenta_repo: CuentaRepository,
        tercero_repo: TerceroRepository,
        centro_costo_repo: CentroCostoRepository,
    ) -> None:
        """Inicializa el servicio de asientos con todos sus repositorios

        colaboradores.
        """
        self._db = db
        self._asiento_repo = asiento_repo
        self._movimiento_repo = movimiento_repo
        self._periodo_repo = periodo_repo
        self._tipo_asiento_repo = tipo_asiento_repo
        self._cuenta_repo = cuenta_repo
        self._tercero_repo = tercero_repo
        self._centro_costo_repo = centro_costo_repo

    async def crear_asiento(
        self, id_periodo: int, datos: AsientoCreate
    ) -> AsientoDetalleOut:
        """Registra un asiento en estado BORRADOR junto con sus movimientos (RF-06, 08,
        12).
        """
        async with self._db.transaccion() as sesion:
            periodo = await self._validar_periodo_abierto(sesion, id_periodo)
            self._validar_fecha_en_periodo(datos.fecha, periodo)

            tipo_asiento = await self._tipo_asiento_repo.obtener_por_id(
                sesion, datos.id_tipo_asiento
            )
            if tipo_asiento is None:
                raise NoEncontrado(
                    f"El tipo de asiento con id_tipo_asiento={datos.id_tipo_asiento} "
                    "no existe."
                )

            duplicado = await self._asiento_repo.obtener_por_numero_periodo(
                sesion, id_periodo=id_periodo, numero=datos.numero
            )
            if duplicado is not None:
                raise Conflicto(
                    f"Ya existe un asiento con número {datos.numero} en el periodo "
                    f"id_periodo={id_periodo}."
                )

            id_empresa = int(periodo["id_empresa"])
            await self._validar_movimientos_contra_empresa(
                sesion,
                id_empresa=id_empresa,
                movimientos=datos.movimientos,
            )

            cabecera = await self._asiento_repo.crear(
                sesion,
                id_periodo=id_periodo,
                id_tipo_asiento=datos.id_tipo_asiento,
                numero=datos.numero,
                fecha=datos.fecha,
                descripcion=datos.descripcion,
                estado="BORRADOR",
            )
            if cabecera is None:
                raise Conflicto("No fue posible registrar el asiento contable.")

            id_asiento = int(cabecera["id_asiento"])
            movimientos_creados: list[MovimientoOut] = []
            for mov in datos.movimientos:
                fila_mov = await self._movimiento_repo.crear(
                    sesion,
                    id_asiento=id_asiento,
                    id_cuenta=mov.id_cuenta,
                    id_tercero=mov.id_tercero,
                    id_centro_costo=mov.id_centro_costo,
                    debe=mov.debe,
                    haber=mov.haber,
                )
                if fila_mov is not None:
                    movimientos_creados.append(MovimientoOut.model_validate(fila_mov))

            cabecera.setdefault("tipo_asiento", tipo_asiento.get("nombre"))
            return self._ensamblar_detalle_asiento(cabecera, movimientos_creados)

    async def listar_asientos_periodo(self, id_periodo: int) -> list[AsientoResumenOut]:
        """Lista los asientos registrados en un periodo contable (RF-15)."""
        async with self._db.conexion() as sesion:
            periodo = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
            if periodo is None:
                raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")
            filas = await self._asiento_repo.listar_por_periodo(sesion, id_periodo)
        return [AsientoResumenOut.model_validate(fila) for fila in filas]

    async def obtener_asiento(self, id_asiento: int) -> AsientoDetalleOut:
        """Obtiene el detalle de un asiento junto con sus movimientos y totales

        (RF-15).
        """
        async with self._db.conexion() as sesion:
            cabecera = await self._asiento_repo.obtener_por_id(sesion, id_asiento)
            if cabecera is None:
                raise NoEncontrado(f"El asiento con id_asiento={id_asiento} no existe.")
            filas_mov = await self._movimiento_repo.listar_por_asiento(
                sesion, id_asiento
            )
        movimientos = [MovimientoOut.model_validate(fila) for fila in filas_mov]
        return self._ensamblar_detalle_asiento(cabecera, movimientos)

    async def actualizar_asiento(
        self, id_asiento: int, datos: AsientoUpdate
    ) -> AsientoDetalleOut:
        """Modifica un asiento en estado BORRADOR de un periodo ABIERTO (RF-12,

        S-15).
        """
        async with self._db.transaccion() as sesion:
            cabecera_actual = await self._asiento_repo.obtener_por_id(
                sesion, id_asiento
            )
            if cabecera_actual is None:
                raise NoEncontrado(f"El asiento con id_asiento={id_asiento} no existe.")
            if cabecera_actual.get("estado") != "BORRADOR":
                raise Conflicto(
                    f"El asiento id_asiento={id_asiento} está CONTABILIZADO y no puede "
                    "modificarse."
                )

            id_periodo = int(cabecera_actual["id_periodo"])
            periodo = await self._validar_periodo_abierto(sesion, id_periodo)
            self._validar_fecha_en_periodo(datos.fecha, periodo)

            tipo_asiento = await self._tipo_asiento_repo.obtener_por_id(
                sesion, datos.id_tipo_asiento
            )
            if tipo_asiento is None:
                raise NoEncontrado(
                    f"El tipo de asiento con id_tipo_asiento={datos.id_tipo_asiento} "
                    "no existe."
                )

            id_empresa = int(periodo["id_empresa"])
            await self._validar_movimientos_contra_empresa(
                sesion,
                id_empresa=id_empresa,
                movimientos=datos.movimientos,
            )

            cabecera_actualizada = await self._asiento_repo.actualizar_cabecera(
                sesion,
                id_asiento=id_asiento,
                id_tipo_asiento=datos.id_tipo_asiento,
                fecha=datos.fecha,
                descripcion=datos.descripcion,
            )
            if cabecera_actualizada is None:
                raise Conflicto("No fue posible actualizar el asiento.")

            await self._movimiento_repo.eliminar_por_asiento(sesion, id_asiento)
            movimientos_nuevos: list[MovimientoOut] = []
            for mov in datos.movimientos:
                fila_mov = await self._movimiento_repo.crear(
                    sesion,
                    id_asiento=id_asiento,
                    id_cuenta=mov.id_cuenta,
                    id_tercero=mov.id_tercero,
                    id_centro_costo=mov.id_centro_costo,
                    debe=mov.debe,
                    haber=mov.haber,
                )
                if fila_mov is not None:
                    movimientos_nuevos.append(MovimientoOut.model_validate(fila_mov))

            cabecera_actualizada.setdefault("tipo_asiento", tipo_asiento.get("nombre"))
            return self._ensamblar_detalle_asiento(
                cabecera_actualizada, movimientos_nuevos
            )

    async def contabilizar_asiento(self, id_asiento: int) -> AsientoDetalleOut:
        """Valida partida doble estricta y cambia el asiento a CONTABILIZADO (RF-07,
        RF-09,
        S-01).
        """
        async with self._db.transaccion() as sesion:
            cabecera = await self._asiento_repo.obtener_por_id(sesion, id_asiento)
            if cabecera is None:
                raise NoEncontrado(f"El asiento con id_asiento={id_asiento} no existe.")
            if cabecera.get("estado") == "CONTABILIZADO":
                raise Conflicto(
                    f"El asiento id_asiento={id_asiento} ya se encuentra CONTABILIZADO."
                )

            id_periodo = int(cabecera["id_periodo"])
            await self._validar_periodo_abierto(sesion, id_periodo)

            filas_mov = await self._movimiento_repo.listar_por_asiento(
                sesion, id_asiento
            )
            if len(filas_mov) < 2:
                raise ReglaDeNegocio(
                    "Un asiento requiere al menos dos movimientos para cumplir la "
                    "partida doble."
                )

            movimientos = [MovimientoOut.model_validate(fila) for fila in filas_mov]
            total_debe = sum((m.debe for m in movimientos), start=CERO)
            total_haber = sum((m.haber for m in movimientos), start=CERO)

            if total_debe <= CERO or total_haber <= CERO:
                raise ReglaDeNegocio(
                    "Los totales de débito y crédito deben ser mayores que cero."
                )
            if total_debe != total_haber:
                raise ReglaDeNegocio(
                    "El asiento no cumple la regla de partida doble (RF-07, S-01): "
                    f"suma debe ({total_debe}) != suma haber ({total_haber})."
                )

            actualizado = await self._asiento_repo.actualizar_estado(
                sesion, id_asiento=id_asiento, estado="CONTABILIZADO"
            )
            if actualizado is None:
                raise Conflicto("No fue posible contabilizar el asiento.")

            actualizado.setdefault("tipo_asiento", cabecera.get("tipo_asiento"))
            return self._ensamblar_detalle_asiento(actualizado, movimientos)

    async def _validar_periodo_abierto(
        self, sesion: SesionBD, id_periodo: int
    ) -> FilaDict:
        """Verifica que el periodo exista y su estado sea ABIERTO (RF-12, S-15)."""
        periodo = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
        if periodo is None:
            raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")
        if periodo.get("estado") == "CERRADO":
            raise Conflicto(
                f"El periodo id_periodo={id_periodo} está CERRADO y no permite crear "
                "ni modificar asientos (RF-12, S-15)."
            )
        return periodo

    @staticmethod
    def _validar_fecha_en_periodo(fecha: date, periodo: FilaDict) -> None:
        """Verifica que la fecha del asiento esté dentro del rango del periodo

        (S-14).
        """
        fecha_inicio: date = periodo["fecha_inicio"]
        fecha_fin: date = periodo["fecha_fin"]
        if not (fecha_inicio <= fecha <= fecha_fin):
            raise ReglaDeNegocio(
                f"La fecha del asiento ({fecha}) está fuera del rango del periodo "
                f"[{fecha_inicio}, {fecha_fin}] (S-14)."
            )

    async def _validar_movimientos_contra_empresa(
        self,
        sesion: SesionBD,
        *,
        id_empresa: int,
        movimientos: list[MovimientoCreate],
    ) -> None:
        """Valida cuenta hoja, tercero y centro de costo de cada movimiento (RF-05,
        S-05,
        S-06, S-21).
        """
        for idx, mov in enumerate(movimientos, start=1):
            if (mov.debe > CERO) == (mov.haber > CERO):
                raise ReglaDeNegocio(
                    f"Movimiento #{idx}: solo uno entre debe y haber puede ser "
                    "distinto de cero (S-21)."
                )

            cuenta = await self._cuenta_repo.obtener_por_id(sesion, mov.id_cuenta)
            if cuenta is None:
                raise NoEncontrado(
                    f"Movimiento #{idx}: la cuenta id_cuenta={mov.id_cuenta} no existe."
                )
            if int(cuenta["id_empresa"]) != id_empresa:
                raise ReglaDeNegocio(
                    f"Movimiento #{idx}: la cuenta id_cuenta={mov.id_cuenta} no "
                    "pertenece a la misma empresa del periodo (S-06, S-18)."
                )
            if not bool(cuenta.get("acepta_movimiento")):
                raise ReglaDeNegocio(
                    f"Movimiento #{idx}: la cuenta '{cuenta.get('codigo')}' no acepta "
                    "movimientos directos (RF-05, S-05)."
                )

            if mov.id_tercero is not None:
                tercero = await self._tercero_repo.obtener_por_id(
                    sesion, mov.id_tercero
                )
                if tercero is None:
                    raise NoEncontrado(
                        f"Movimiento #{idx}: el tercero id_tercero={mov.id_tercero} no "
                        "existe."
                    )
                if int(tercero["id_empresa"]) != id_empresa:
                    raise ReglaDeNegocio(
                        f"Movimiento #{idx}: el tercero id_tercero={mov.id_tercero} "
                        "pertenece a otra empresa (S-06)."
                    )

            if mov.id_centro_costo is not None:
                centro = await self._centro_costo_repo.obtener_por_id(
                    sesion, mov.id_centro_costo
                )
                if centro is None:
                    raise NoEncontrado(
                        f"Movimiento #{idx}: el centro de costo "
                        f"id_centro_costo={mov.id_centro_costo} no existe."
                    )
                if int(centro["id_empresa"]) != id_empresa:
                    raise ReglaDeNegocio(
                        f"Movimiento #{idx}: el centro de costo "
                        f"id_centro_costo={mov.id_centro_costo} pertenece a otra "
                        "empresa (S-06)."
                    )

    @staticmethod
    def _ensamblar_detalle_asiento(
        cabecera: FilaDict, movimientos: list[MovimientoOut]
    ) -> AsientoDetalleOut:
        """Calcula totales de débito/crédito y construye el DTO detallado."""
        total_debe = sum((m.debe for m in movimientos), start=CERO)
        total_haber = sum((m.haber for m in movimientos), start=CERO)
        cuadra = total_debe > CERO and total_debe == total_haber
        return AsientoDetalleOut(
            id_asiento=int(cabecera["id_asiento"]),
            id_periodo=int(cabecera["id_periodo"]),
            id_tipo_asiento=int(cabecera["id_tipo_asiento"]),
            tipo_asiento=cabecera.get("tipo_asiento"),
            numero=int(cabecera["numero"]),
            fecha=cabecera["fecha"],
            descripcion=str(cabecera["descripcion"]),
            estado=cabecera["estado"],
            total_debe=total_debe,
            total_haber=total_haber,
            cuadra=cuadra,
            movimientos=movimientos,
        )
