from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import pilotos

app = FastAPI(title="DB Unbosque API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(pilotos.router)


@app.get("/health")
def health():
    return {"status": "ok"}
