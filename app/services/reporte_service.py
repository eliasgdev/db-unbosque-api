"""Servicio de negocio para Estado de Resultados y Balance General (RF-09, RF-13, RF-14,
RF-15).

Implementa las reglas S-07, S-08, S-09, S-10 y S-11:
- Los saldos y reportes se calculan al vuelo sin almacenarse en base de datos (S-07).
- Solo se incluyen movimientos de asientos en estado CONTABILIZADO (RF-09, S-08).
- La estructura de presentación de ambos estados la determina RUBRO_ESTADO (S-11).
- El Balance General integra la utilidad del ejercicio en curso y verifica
  la ecuación patrimonial Activo = Pasivo + Patrimonio (RF-14, S-09).
"""

from datetime import date
from decimal import Decimal

from app.core.database import FilaDict, GestorBaseDatos
from app.core.exceptions import NoEncontrado
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.rubro_estado_repository import RubroEstadoRepository
from app.schemas.reportes import (
    BalanceGeneralOut,
    EstadoResultadosOut,
    RubroReporteOut,
    SaldoCuentaReporteOut,
)

CERO = Decimal("0.00")
CLASES_NATURALEZA_CREDITO = frozenset({"PASIVO", "PATRIMONIO", "INGRESO"})


class ReporteService:
    """Genera el Estado de Resultados por periodo y el Balance General a fecha de

    corte.
    """

    def __init__(
        self,
        db: GestorBaseDatos,
        reporte_repo: ReporteRepository,
        periodo_repo: PeriodoRepository,
        empresa_repo: EmpresaRepository,
        rubro_repo: RubroEstadoRepository,
    ) -> None:
        """Inicializa el servicio de reportes contables."""
        self._db = db
        self._reporte_repo = reporte_repo
        self._periodo_repo = periodo_repo
        self._empresa_repo = empresa_repo
        self._rubro_repo = rubro_repo

    async def generar_estado_resultados(self, id_periodo: int) -> EstadoResultadosOut:
        """Calcula el Estado de Resultados para un periodo contable (RF-13, S-10,

        S-11).
        """
        async with self._db.conexion() as sesion:
            periodo = await self._periodo_repo.obtener_por_id(sesion, id_periodo)
            if periodo is None:
                raise NoEncontrado(f"El periodo con id_periodo={id_periodo} no existe.")

            rubros_filas = await self._rubro_repo.listar_por_estado_financiero(
                sesion, "RESULTADOS"
            )
            saldos_filas = await self._reporte_repo.obtener_saldos_resultados_periodo(
                sesion, id_periodo
            )

        ingresos = CERO
        costos = CERO
        gastos = CERO
        gastos_operacionales = CERO

        codigos_operacionales = {
            int(r["id_rubro"])
            for r in rubros_filas
            if "OPER" in str(r.get("codigo", "")).upper()
            or "OPER" in str(r.get("nombre", "")).upper()
        }

        cuentas_por_rubro: dict[int, list[SaldoCuentaReporteOut]] = {}
        for fila in saldos_filas:
            saldo = self._calcular_saldo_segun_naturaleza(fila)
            clase = str(fila["clase"])
            id_rubro = int(fila["id_rubro"])

            if clase == "INGRESO":
                ingresos += saldo
            elif clase == "COSTO":
                costos += saldo
            elif clase == "GASTO":
                gastos += saldo
                if not codigos_operacionales or id_rubro in codigos_operacionales:
                    gastos_operacionales += saldo

            cuenta_dto = SaldoCuentaReporteOut(
                id_cuenta=int(fila["id_cuenta"]),
                codigo=str(fila["codigo"]),
                nombre=str(fila["nombre"]),
                clase=clase,
                naturaleza=str(fila["naturaleza"]),
                saldo=saldo,
            )
            cuentas_por_rubro.setdefault(id_rubro, []).append(cuenta_dto)

        utilidad_bruta = ingresos - costos
        utilidad_operacional = utilidad_bruta - gastos_operacionales
        utilidad_neta = ingresos - costos - gastos

        arbol_rubros = self._construir_arbol_rubros(rubros_filas, cuentas_por_rubro)

        return EstadoResultadosOut(
            id_periodo=int(periodo["id_periodo"]),
            id_empresa=int(periodo["id_empresa"]),
            fecha_inicio=periodo["fecha_inicio"],
            fecha_fin=periodo["fecha_fin"],
            ingresos=ingresos,
            costos=costos,
            gastos=gastos,
            utilidad_bruta=utilidad_bruta,
            utilidad_operacional=utilidad_operacional,
            utilidad_neta=utilidad_neta,
            rubros=arbol_rubros,
        )

    async def generar_balance_general(
        self, id_empresa: int, fecha_corte: date
    ) -> BalanceGeneralOut:
        """Calcula el Balance General clasificado a una fecha de corte (RF-14, S-09,

        S-11).
        """
        async with self._db.conexion() as sesion:
            empresa = await self._empresa_repo.obtener_por_id(sesion, id_empresa)
            if empresa is None:
                raise NoEncontrado(f"La empresa con id_empresa={id_empresa} no existe.")

            rubros_filas = await self._rubro_repo.listar_por_estado_financiero(
                sesion, "BALANCE"
            )
            saldos_filas = await self._reporte_repo.obtener_saldos_balance_a_corte(
                sesion, id_empresa=id_empresa, fecha_corte=fecha_corte
            )
            fila_utilidad = await self._reporte_repo.obtener_utilidad_ejercicio_a_corte(
                sesion, id_empresa=id_empresa, fecha_corte=fecha_corte
            )

        total_activo = CERO
        total_pasivo = CERO
        patrimonio_cuentas = CERO

        cuentas_por_rubro: dict[int, list[SaldoCuentaReporteOut]] = {}
        for fila in saldos_filas:
            saldo = self._calcular_saldo_segun_naturaleza(fila)
            clase = str(fila["clase"])
            id_rubro = int(fila["id_rubro"])

            if clase == "ACTIVO":
                total_activo += saldo
            elif clase == "PASIVO":
                total_pasivo += saldo
            elif clase == "PATRIMONIO":
                patrimonio_cuentas += saldo

            cuenta_dto = SaldoCuentaReporteOut(
                id_cuenta=int(fila["id_cuenta"]),
                codigo=str(fila["codigo"]),
                nombre=str(fila["nombre"]),
                clase=clase,
                naturaleza=str(fila["naturaleza"]),
                saldo=saldo,
            )
            cuentas_por_rubro.setdefault(id_rubro, []).append(cuenta_dto)

        utilidad_ejercicio = CERO
        if fila_utilidad is not None:
            ing = Decimal(str(fila_utilidad.get("total_ingresos") or "0.00"))
            cos = Decimal(str(fila_utilidad.get("total_costos") or "0.00"))
            gas = Decimal(str(fila_utilidad.get("total_gastos") or "0.00"))
            utilidad_ejercicio = ing - cos - gas

        total_patrimonio = patrimonio_cuentas + utilidad_ejercicio
        diferencia_ecuacion = total_activo - (total_pasivo + total_patrimonio)
        cuadra = diferencia_ecuacion == CERO

        arbol_rubros = self._construir_arbol_rubros(rubros_filas, cuentas_por_rubro)

        return BalanceGeneralOut(
            id_empresa=int(empresa["id_empresa"]),
            razon_social=str(empresa["razon_social"]),
            fecha_corte=fecha_corte,
            total_activo=total_activo,
            total_pasivo=total_pasivo,
            total_patrimonio=total_patrimonio,
            utilidad_ejercicio=utilidad_ejercicio,
            diferencia_ecuacion=diferencia_ecuacion,
            cuadra=cuadra,
            rubros=arbol_rubros,
        )

    @staticmethod
    def _calcular_saldo_segun_naturaleza(fila: FilaDict) -> Decimal:
        """Calcula el saldo de una cuenta con el signo de la naturaleza de su clase.

        Se usa la naturaleza propia de la clase (ACTIVO/COSTO/GASTO = DEBITO;
        PASIVO/PATRIMONIO/INGRESO = CREDITO) y no la de la cuenta, para que las
        contracuentas (ej. Depreciación Acumulada: ACTIVO con naturaleza CREDITO)
        resten del total de su clase y de los subtotales de su rubro.
        """
        debe = Decimal(str(fila.get("total_debe") or "0.00"))
        haber = Decimal(str(fila.get("total_haber") or "0.00"))
        clase = str(fila.get("clase") or "").upper()
        if clase in CLASES_NATURALEZA_CREDITO:
            return haber - debe
        return debe - haber

    def _construir_arbol_rubros(
        self,
        rubros_filas: list[FilaDict],
        cuentas_por_rubro: dict[int, list[SaldoCuentaReporteOut]],
    ) -> list[RubroReporteOut]:
        """Arma la jerarquía recursiva de RUBRO_ESTADO y acumula los subtotales

        (S-11).
        """
        nodos: dict[int, RubroReporteOut] = {}
        raices: list[RubroReporteOut] = []

        rubros_ordenados = sorted(
            rubros_filas, key=lambda r: (int(r.get("orden", 0)), int(r["id_rubro"]))
        )

        for fila in rubros_ordenados:
            id_rubro = int(fila["id_rubro"])
            cuentas = cuentas_por_rubro.get(id_rubro, [])
            subtotal_propio = sum((c.saldo for c in cuentas), start=CERO)
            nodo = RubroReporteOut(
                id_rubro=id_rubro,
                id_rubro_padre=(
                    int(fila["id_rubro_padre"])
                    if fila.get("id_rubro_padre") is not None
                    else None
                ),
                codigo=str(fila["codigo"]),
                nombre=str(fila["nombre"]),
                orden=int(fila["orden"]),
                subtotal=subtotal_propio,
                cuentas=cuentas,
                subrubros=[],
            )
            nodos[id_rubro] = nodo

        for nodo in nodos.values():
            if nodo.id_rubro_padre is not None and nodo.id_rubro_padre in nodos:
                nodos[nodo.id_rubro_padre].subrubros.append(nodo)
            else:
                raices.append(nodo)

        for raiz in raices:
            self._recalcular_subtotal_recursivo(raiz)

        return raices

    def _recalcular_subtotal_recursivo(self, rubro: RubroReporteOut) -> Decimal:
        """Suma recursivamente los saldos de cuentas propias y de los subrubros

        hijos.
        """
        subtotal_cuentas = sum((c.saldo for c in rubro.cuentas), start=CERO)
        subtotal_hijos = sum(
            (self._recalcular_subtotal_recursivo(hijo) for hijo in rubro.subrubros),
            start=CERO,
        )
        rubro.subtotal = subtotal_cuentas + subtotal_hijos
        return rubro.subtotal
