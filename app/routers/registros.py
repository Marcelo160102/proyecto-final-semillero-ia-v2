from fastapi import APIRouter, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import obtener_config
from app.models import SolicitudLegal
from app.templating import templates

router = APIRouter(tags=["registros"])

config = obtener_config()
sync_engine = create_engine(config.database_url.replace("+aiosqlite", ""))


@router.get("/registros")
async def pagina_registros(request: Request):
    with Session(sync_engine) as session:
        registros = (
            session.query(SolicitudLegal)
            .order_by(SolicitudLegal.fecha_creacion.desc())
            .all()
        )

    return templates.TemplateResponse(
        request, "registros.html", {"registros": registros}
    )
