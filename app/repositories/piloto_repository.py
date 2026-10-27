from app.core.database import fetch_all, fetch_one

BASE_QUERY = "SELECT id, nombre, apellido, nacionalidad, fecha_nacimiento FROM piloto"


def listar() -> list[dict]:
    return fetch_all(BASE_QUERY)


def obtener(piloto_id: int) -> dict | None:
    return fetch_one(f"{BASE_QUERY} WHERE id = :id", {"id": piloto_id})
