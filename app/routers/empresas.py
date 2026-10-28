from fastapi import APIRouter, HTTPException

from app.repositories import empresa_repository
from app.schemas.contabilidad import Cuenta, Empresa, Periodo

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get("", response_model=list[Empresa])
def listar():
    return empresa_repository.listar()


@router.get("/{nit}", response_model=Empresa)
def obtener(nit: str):
    empresa = empresa_repository.obtener(nit)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


@router.get("/{nit}/periodos", response_model=list[Periodo])
def periodos(nit: str):
    return empresa_repository.periodos(nit)


@router.get("/{nit}/cuentas", response_model=list[Cuenta])
def cuentas(nit: str):
    return empresa_repository.cuentas(nit)
