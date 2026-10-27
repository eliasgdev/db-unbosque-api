from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def fetch_all(query: str, params: dict | None = None) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return [dict(row) for row in result.mappings()]


def fetch_one(query: str, params: dict | None = None) -> dict | None:
    rows = fetch_all(query, params)
    return rows[0] if rows else None
