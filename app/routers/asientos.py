from fastapi import APIRouter

from app.repositories import asiento_repository
from app.schemas.contabilidad import Asiento, Movimiento

router = APIRouter(tags=["asientos"])


@router.get("/periodos/{periodo_id}/asientos", response_model=list[Asiento])
def por_periodo(periodo_id: int):
    return asiento_repository.por_periodo(periodo_id)


@router.get("/asientos/{asiento_id}/movimientos", response_model=list[Movimiento])
def movimientos(asiento_id: int):
    return asiento_repository.movimientos(asiento_id)
