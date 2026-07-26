from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers import admin, chat, registros


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        from app.phoenix_setup import setup_phoenix

        setup_phoenix()
    except Exception as exc:
        import logging

        logging.warning("Phoenix no disponible: %s", exc)
    try:
        from app.services.embedding_service import verificar_indexacion

        verificar_indexacion()
    except Exception as exc:
        import logging

        logging.warning("Indexacion automatica fallo: %s", exc)
    yield
    await engine.dispose()


app = FastAPI(
    title="Mesa de Ayuda Legal - Patito S.A.",
    description="Sistema multi-agente IA para el Departamento Legal de Patito S.A.",
    version="2.0.0",
    lifespan=lifespan,
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
uploads_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(chat.router)
app.include_router(registros.router)
app.include_router(admin.router)
