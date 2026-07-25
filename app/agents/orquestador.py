import uuid

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.agents.base import extraer_texto
from app.agents.herramientas import TOOLS_ORQUESTADOR
from app.services.llm_service import obtener_llm

SYSTEM_PROMPT_ORQUESTADOR = """Eres el orquestador de la Mesa de Ayuda Legal de Patito S.A. Coordinas agentes especializados:

- consultar_contratos: para preguntas sobre contratos (cláusulas, tipos, plazos, proceso de firma).
- consultar_proteccion_datos: para preguntas sobre protección de datos personales.
- consultar_cumplimiento: para preguntas sobre cumplimiento normativo y ética.
- analizar_documento_legal_tool: cuando el usuario indique la RUTA de una imagen de un documento legal.
- registrar_solicitud_legal_tool: para REGISTRAR / GUARDAR / CREAR una solicitud de elaboración o revisión de contrato.

Reglas de ruteo:
- Identifica el tema de la pregunta y usa la tool correspondiente.
- Si la pregunta abarca MÚLTIPLES temas (ej. contratos + datos), invoca TODAS las tools necesarias para cubrir la consulta completa.
- Cuando invoques múltiples tools, consolida las respuestas parciales en una respuesta final coherente.
- Para registrar una solicitud, necesitas: tipo_contrato, proveedor, objeto, plazo, monto y trata_datos_personales.
- Si falta algún dato obligatorio, PÍDELO al usuario. Nunca registres con datos incompletos.
- Cuando recibas confirmación del usuario, llama a registrar_solicitud_legal_tool con confirmado=True.
- Si el usuario da la ruta de una imagen, usa analizar_documento_legal_tool.
- Si no tienes la información suficiente, dilo; no inventes."""


def crear_orquestador():
    llm = obtener_llm()
    memoria = InMemorySaver()
    return create_agent(
        model=llm,
        tools=TOOLS_ORQUESTADOR,
        system_prompt=SYSTEM_PROMPT_ORQUESTADOR,
        checkpointer=memoria,
    )


orquestador = crear_orquestador()


def _extraer_trazas(
    resultado: dict,
) -> dict:
    agentes_vistos: set[str] = set()
    trazas: list[dict] = []
    respuesta_final = ""

    for m in resultado["messages"]:
        tc = getattr(m, "tool_calls", None)
        if tc:
            for t in tc:
                agentes_vistos.add(t["name"])
                trazas.append({
                    "tipo": "accion",
                    "tool": t["name"],
                    "args": t["args"],
                })

        if m.type == "tool":
            trazas.append({
                "tipo": "obs",
                "tool": m.name,
                "preview": extraer_texto(m.content)[:250].replace("\n", " "),
            })

        if m.type == "ai" and m.content and not tc:
            respuesta_final = extraer_texto(m.content)

    return {
        "respuesta": respuesta_final,
        "agentes": sorted(agentes_vistos),
        "trazas": trazas,
        "raw": resultado,
    }


def consultar(pregunta: str, thread_id: str | None = None):
    thread_id = thread_id or f"legal-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    resultado = orquestador.invoke(
        {"messages": [{"role": "user", "content": pregunta}]}, config
    )

    return _extraer_trazas(resultado)
