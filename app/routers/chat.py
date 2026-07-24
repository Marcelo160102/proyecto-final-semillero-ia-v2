import asyncio
import json

from fastapi import APIRouter, Form, Request
from sqlalchemy import select

from app.agents.orquestador import consultar
from app.database import async_session
from app.models import Consulta
from app.templating import templates

router = APIRouter(tags=["chat"])


@router.get("/")
async def pagina_chat(request: Request):
    async with async_session() as session:
        stmt = (
            select(Consulta)
            .order_by(Consulta.fecha_creacion.desc())
            .limit(20)
        )
        result = await session.execute(stmt)
        historial = result.scalars().all()

    return templates.TemplateResponse(
        request, "index.html", {"historial": historial}
    )


@router.post("/chat")
async def enviar_consulta(request: Request, pregunta: str = Form(...)):
    loop = asyncio.get_event_loop()
    resultado = await loop.run_in_executor(None, consultar, pregunta)

    async with async_session() as session:
        consulta = Consulta(
            pregunta=pregunta,
            respuesta=resultado["respuesta"],
            agentes_participantes=json.dumps(resultado["agentes"], ensure_ascii=False),
            fuentes=json.dumps(resultado["trazas"], ensure_ascii=False),
        )
        session.add(consulta)
        await session.commit()

    response = templates.TemplateResponse(
        request,
        "fragments/mensaje_chat.html",
        {"pregunta": pregunta, "respuesta": resultado},
    )
    response.headers["HX-Trigger"] = "history-updated"
    return response


@router.get("/historial")
async def historial_fragment(request: Request):
    async with async_session() as session:
        stmt = (
            select(Consulta)
            .order_by(Consulta.fecha_creacion.desc())
            .limit(20)
        )
        result = await session.execute(stmt)
        historial = result.scalars().all()

    return templates.TemplateResponse(
        request, "fragments/historial.html", {"historial": historial}
    )
