from fastapi import APIRouter, HTTPException

from app.repositories import piloto_repository
from app.schemas.piloto import Piloto

router = APIRouter(prefix="/pilotos", tags=["pilotos"])


@router.get("", response_model=list[Piloto])
def listar():
    return piloto_repository.listar()


@router.get("/{piloto_id}", response_model=Piloto)
def obtener(piloto_id: int):
    piloto = piloto_repository.obtener(piloto_id)
    if not piloto:
        raise HTTPException(status_code=404, detail="Piloto no encontrado")
    return piloto
