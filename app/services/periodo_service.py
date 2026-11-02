"""Servicio de negocio para periodos contables y cierre de periodo (RF-02, RF-11,
RF-12).

Implementa la validación de no traslape de fechas (S-13) y la ejecución atómica
del cierre contable en una sola transacción (S-16, S-17).
"""

from datetime import UTC, datetime
from decimal import Decimal

from app.core.database import GestorBaseDatos
from app.core.exceptions import Conflicto, NoEncontrado, ReglaDeNegocio
from app.repositories.asiento_repository import AsientoRepository
from app.repositories.cierre_repository import CierreRepository
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.tipo_asiento_repository import TipoAsientoRepository
from app.schemas.periodo import (
    CierrePeriodoCreate,
    CierrePeriodoOut,
    PeriodoCreate,
    PeriodoOut,
)

CERO = Decimal("0.00")


class PeriodoService:
    """Gestiona los periodos contables y el proceso de cierre de ejercicio."""

    def __init__(
        self,
        db: GestorBaseDatos,
        periodo_repo: PeriodoRepository,
        empresa_repo: EmpresaRepository,
        cierre_repo: CierreRepository,
        cuenta_repo: CuentaRepository,
        asiento_repo: AsientoRepository,
        movimiento_repo: MovimientoRepository,
        tipo_asiento_repo: TipoAsientoRepository,
        reporte_repo: ReporteRepository,
    ) -> None:
        """Inicializa el servicio de periodos con los repositorios requeridos."""
        self._db = db
        self._periodo_repo = periodo_repo
        self._empresa_repo = empresa_repo
        self._cierre_repo = cierre_repo
        self._cuenta_repo = cuenta_repo
        self._asiento_repo = asiento_repo
        self._movimiento_repo = movimiento_repo
        self._tipo_asiento_repo = tipo_asiento_repo
        self._reporte_repo = reporte_repo

    async def crear_periodo(self, id_empresa: int, datos: PeriodoCreate) -> PeriodoOut:
        """Crea un nuevo periodo abierto verificando que no se traslape (RF-02,

        S-13).
        """
        if datos.fecha_fin <= datos.fecha_inicio:
            raise ReglaDeNegocio(
                "La fecha de fin del periodo debe ser mayor que la fecha de inicio."
            )

        async with self._db.transaccion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")

            traslape = await self._periodo_repo.buscar_traslape(
                sesion,
                id_empresa=id_empresa,
                fecha_inicio=datos.fecha_inicio,
                fecha_fin=datos.fecha_fin,
            )
            if traslape is not None:
                raise Conflicto(
                    "El rango de fechas indicado se traslapa con un periodo "
                    f"existente (id_periodo={traslape.get('id_periodo')}) "
                    "de la misma empresa (S-13)."
                )

            creado = await self._periodo_repo.crear(
                sesion,
                id_empresa=id_empresa,
                fecha_inicio=datos.fecha_inicio,
                fecha_fin=datos.fecha_fin,
                estado="ABIERTO",
            )
            if creado is None:
                raise Conflicto("No fue posible registrar el periodo contable.")
            return PeriodoOut.model_validate(creado)

    async def listar_periodos_empresa(self, id_empresa: int) -> list[PeriodoOut]:
        """Lista todos los periodos contables de una empresa (RF-02, RF-15)."""
        async with self._db.conexion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")
            filas = await self._periodo_repo.listar_por_empresa(sesion, id_empresa)
        return [PeriodoOut.model_validate(fila) for fila in filas]

    async def obtener_periodo(self, id_periodo: int) -> PeriodoOut:
        """Consulta un periodo contable por su identificador (RF-02, RF-15)."""
        async with self._db.conexion() as sesion:
            fila = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
        if fila is None:
            raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")
        return PeriodoOut.model_validate(fila)

    async def cerrar_periodo(
        self, id_periodo: int, datos: CierrePeriodoCreate
    ) -> CierrePeriodoOut:
        """Ejecuta el cierre contable atómico de un periodo (RF-11, RF-12, S-16, S-17).

        En una única transacción:
        1. Verifica que el periodo exista y esté ABIERTO (sin cierre previo).
        2. Valida que la cuenta de patrimonio destino pertenezca a la misma empresa,
           sea de clase PATRIMONIO y acepte movimiento.
        3. Calcula los saldos de las cuentas de resultado (INGRESO, COSTO, GASTO)
           de asientos CONTABILIZADO en el periodo.
        4. Genera el asiento de tipo CIERRE en estado CONTABILIZADO que salda las
           cuentas de resultado contra la cuenta patrimonial de utilidad/pérdida.
        5. Registra CIERRE_PERIODO y actualiza el periodo a estado CERRADO.
        """
        async with self._db.transaccion() as sesion:
            periodo = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
            if periodo is None:
                raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")
            if periodo.get("estado") == "CERRADO":
                raise Conflicto(
                    f"El periodo id_periodo={id_periodo} ya se encuentra CERRADO "
                    "(S-17)."
                )

            cierre_existente = await self._cierre_repo.obtener_por_periodo(
                sesion, id_periodo
            )
            if cierre_existente is not None:
                raise Conflicto(
                    "Ya existe un registro de cierre para el periodo "
                    f"id_periodo={id_periodo}."
                )

            asientos_periodo = await self._asiento_repo.listar_por_periodo(
                sesion, id_periodo
            )
            borradores = [a for a in asientos_periodo if a.get("estado") == "BORRADOR"]
            if borradores:
                numeros = ", ".join(str(a["numero"]) for a in borradores)
                raise ReglaDeNegocio(
                    "No se puede cerrar el periodo: tiene "
                    f"{len(borradores)} asiento(s) en BORRADOR (números {numeros}). "
                    "Contabilícelos o corríjalos antes del cierre."
                )

            id_empresa = int(periodo["id_empresa"])
            cuenta_pat = await self._cuenta_repo.obtener_por_id(
                sesion, datos.id_cuenta_patrimonio
            )
            if cuenta_pat is None:
                raise NoEncontrado(
                    f"La cuenta de patrimonio id_cuenta={datos.id_cuenta_patrimonio} "
                    "no existe."
                )
            if int(cuenta_pat["id_empresa"]) != id_empresa:
                raise ReglaDeNegocio(
                    "La cuenta de patrimonio debe pertenecer a la misma empresa del "
                    "periodo (S-06)."
                )
            if not bool(cuenta_pat.get("acepta_movimiento")):
                raise ReglaDeNegocio(
                    "La cuenta de patrimonio para el cierre debe aceptar movimiento "
                    "(RF-05)."
                )
            clase_pat = str(cuenta_pat.get("clase_cuenta") or "")
            if clase_pat and clase_pat != "PATRIMONIO":
                raise ReglaDeNegocio(
                    "La cuenta destino de la utilidad del ejercicio debe ser de clase "
                    "PATRIMONIO."
                )

            saldos_resultado = await self._reporte_repo.obtener_saldos_para_cierre(
                sesion, id_periodo
            )

            total_ingresos = CERO
            total_costos = CERO
            total_gastos = CERO
            movimientos_cierre: list[tuple[int, Decimal, Decimal]] = []

            for fila in saldos_resultado:
                id_cuenta = int(fila["id_cuenta"])
                clase = str(fila["clase"])
                debe_acum = Decimal(str(fila.get("total_debe") or "0.00"))
                haber_acum = Decimal(str(fila.get("total_haber") or "0.00"))
                diferencia = debe_acum - haber_acum

                if clase == "INGRESO":
                    total_ingresos += haber_acum - debe_acum
                elif clase == "COSTO":
                    total_costos += debe_acum - haber_acum
                elif clase == "GASTO":
                    total_gastos += debe_acum - haber_acum

                if diferencia > CERO:
                    # Saldo débito -> se acredita para dejar en cero
                    movimientos_cierre.append((id_cuenta, CERO, diferencia))
                elif diferencia < CERO:
                    # Saldo crédito -> se debita para dejar en cero
                    movimientos_cierre.append((id_cuenta, abs(diferencia), CERO))

            utilidad_neta = total_ingresos - total_costos - total_gastos
            if utilidad_neta > CERO:
                # Utilidad positiva -> aumenta el patrimonio (crédito)
                movimientos_cierre.append(
                    (datos.id_cuenta_patrimonio, CERO, utilidad_neta)
                )
            elif utilidad_neta < CERO:
                # Pérdida del ejercicio -> disminuye el patrimonio (débito)
                movimientos_cierre.append(
                    (datos.id_cuenta_patrimonio, abs(utilidad_neta), CERO)
                )

            id_asiento_cierre: int | None = None
            if movimientos_cierre:
                suma_debe = sum((m[1] for m in movimientos_cierre), start=CERO)
                suma_haber = sum((m[2] for m in movimientos_cierre), start=CERO)
                if suma_debe != suma_haber:
                    raise ReglaDeNegocio(
                        "El asiento automático de cierre no cumple la partida doble: "
                        f"debe={suma_debe} vs haber={suma_haber}."
                    )

                tipo_cierre = await self._tipo_asiento_repo.obtener_por_nombre(
                    sesion, "CIERRE"
                )
                if tipo_cierre is None:
                    raise NoEncontrado(
                        "No se encontró el tipo de asiento 'CIERRE' en el catálogo "
                        "TIPO_ASIENTO."
                    )

                siguiente_numero = await self._asiento_repo.obtener_siguiente_numero(
                    sesion, id_periodo
                )
                asiento_creado = await self._asiento_repo.crear(
                    sesion,
                    id_periodo=id_periodo,
                    id_tipo_asiento=int(tipo_cierre["id_tipo_asiento"]),
                    numero=siguiente_numero,
                    fecha=periodo["fecha_fin"],
                    descripcion=datos.descripcion_asiento,
                    estado="CONTABILIZADO",
                )
                if asiento_creado is None:
                    raise Conflicto("No fue posible generar el asiento de cierre.")

                id_asiento_cierre = int(asiento_creado["id_asiento"])
                for id_cta, val_debe, val_haber in movimientos_cierre:
                    await self._movimiento_repo.crear(
                        sesion,
                        id_asiento=id_asiento_cierre,
                        id_cuenta=id_cta,
                        id_tercero=None,
                        id_centro_costo=None,
                        debe=val_debe,
                        haber=val_haber,
                    )

            ahora = datetime.now(tz=UTC)
            cierre = await self._cierre_repo.crear(
                sesion,
                id_periodo=id_periodo,
                id_asiento_cierre=id_asiento_cierre,
                utilidad_neta=utilidad_neta,
                fecha_cierre=ahora,
            )
            await self._periodo_repo.actualizar_estado(
                sesion, id_periodo=id_periodo, estado="CERRADO"
            )
            if cierre is None:
                raise Conflicto("No fue posible persistir el registro de cierre.")
            return CierrePeriodoOut.model_validate(cierre)

    async def obtener_cierre_periodo(self, id_periodo: int) -> CierrePeriodoOut:
        """Consulta el registro de cierre y la utilidad trasladada de un periodo

        (RF-11).
        """
        async with self._db.conexion() as sesion:
            periodo = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
            if periodo is None:
                raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")
            cierre = await self._cierre_repo.obtener_por_periodo(sesion, id_periodo)
        if cierre is None:
            raise NoEncontrado(
                f"El periodo con id_periodo={id_periodo} aún no tiene cierre "
                "registrado."
            )
        return CierrePeriodoOut.model_validate(cierre)
