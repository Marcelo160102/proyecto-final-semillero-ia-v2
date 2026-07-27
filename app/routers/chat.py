import asyncio
import json
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, Request, UploadFile
from sqlalchemy import delete, select

from app.agents.orquestador import consultar
from app.monitoring.evaluacion import evaluar_respuesta
from app.db.database import async_session
from app.db.models import Consulta
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
        request, "index.html", {"historial": historial, "seccion_activa": "chat"}
    )


@router.post("/chat")
async def enviar_consulta(
    request: Request,
    pregunta: str = Form(...),
    imagen: UploadFile | None = File(None),
):
    ruta_imagen = None
    if imagen and imagen.filename:
        ext = Path(imagen.filename).suffix or ".png"
        dest = Path("app/static/uploads") / f"chat_{uuid4().hex}{ext}"
        dest.write_bytes(await imagen.read())
        ruta_imagen = str(dest)

    pregunta_final = (
        f"{pregunta}\nRUTA_IMAGEN: {ruta_imagen}"
        if ruta_imagen else pregunta
    )

    loop = asyncio.get_event_loop()
    try:
        resultado = await loop.run_in_executor(None, consultar, pregunta_final)
    except Exception as e:
        logging.error("Error en consulta: %s", e)
        resultado = {
            "respuesta": "Ocurrio un error al procesar tu consulta. Por favor intenta de nuevo mas tarde.",
            "agentes": [],
            "trazas": [],
        }
        contexto = {"pregunta": pregunta, "respuesta": resultado}
        response = templates.TemplateResponse(
            request, "fragments/respuesta_agente.html", contexto,
        )
        response.headers["HX-Trigger"] = "history-updated"
        return response

    try:
        evaluacion = evaluar_respuesta(pregunta, resultado["respuesta"])
        resultado["evaluacion"] = evaluacion
    except Exception:
        resultado["evaluacion"] = None

    async with async_session() as session:
        consulta = Consulta(
            pregunta=pregunta,
            respuesta=resultado["respuesta"],
            agentes_participantes=json.dumps(resultado["agentes"], ensure_ascii=False),
            fuentes=json.dumps(resultado["trazas"], ensure_ascii=False),
            evaluacion=json.dumps(resultado.get("evaluacion"), ensure_ascii=False) if resultado.get("evaluacion") else None,
        )
        session.add(consulta)
        await session.commit()

    contexto = {
        "pregunta": pregunta,
        "respuesta": resultado,
    }
    if ruta_imagen:
        contexto["imagen_url"] = f"/static/uploads/{Path(ruta_imagen).name}"

    response = templates.TemplateResponse(
        request,
        "fragments/respuesta_agente.html",
        contexto,
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


@router.delete("/historial")
async def limpiar_historial():
    async with async_session() as session:
        await session.execute(delete(Consulta))
        await session.commit()
    from starlette.responses import Response
    return Response(headers={"HX-Trigger": "history-updated"})
