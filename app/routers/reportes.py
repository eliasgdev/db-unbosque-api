from datetime import date

from fastapi import APIRouter

from app.schemas.contabilidad import BalanceGeneral, EstadoResultados
from app.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/estado-resultados", response_model=EstadoResultados)
def estado_resultados(periodo_id: int):
    return reporte_service.estado_resultados(periodo_id)


@router.get("/balance-general", response_model=BalanceGeneral)
def balance_general(nit: str, fecha_corte: date):
    return reporte_service.balance_general(nit, fecha_corte)
