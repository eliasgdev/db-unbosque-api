from datetime import date

from pydantic import BaseModel


class Piloto(BaseModel):
    id: int
    nombre: str
    apellido: str
    nacionalidad: str | None = None
    fecha_nacimiento: date | None = None
