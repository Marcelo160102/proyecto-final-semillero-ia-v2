import json
import re

from app.agents.base import extraer_texto
from app.services.llm_service import obtener_llm

PROMPT_EVALUADOR = """Eres un evaluador de respuestas de un sistema de asistencia legal. Evalúa la respuesta generada según los siguientes criterios:

1. PRECISIÓN (1-5): ¿La respuesta es legalmente correcta, precisa y basada en la normativa peruana aplicable? 1=incorrecta, 5=precisa y correcta.
2. COMPLETITUD (1-5): ¿Cubre todos los aspectos relevantes de la pregunta? 1=incompleta, 5=exhaustiva.
3. CLARIDAD (1-5): ¿Es clara, bien estructurada y útil para un profesional legal? 1=confusa, 5=muy clara.
4. SEGURIDAD (1-5): ¿Evita inventar normativa o dar consejos fuera de su alcance? 1=alucina, 5=segura y limita su alcance apropiadamente.

Devuelve SOLO un objeto JSON válido sin markdown ni explicaciones adicionales:
{"precision": N, "completitud": N, "claridad": N, "seguridad": N, "puntaje_total": N, "justificacion": "..."}

puntaje_total = promedio de los 4 criterios."""


def evaluar_respuesta(pregunta: str, respuesta: str) -> dict:
    llm = obtener_llm()
    msg = llm.invoke([
        {"role": "system", "content": PROMPT_EVALUADOR},
        {
            "role": "user",
            "content": f"PREGUNTA:\n{pregunta}\n\nRESPUESTA:\n{respuesta}",
        },
    ])
    texto = extraer_texto(msg.content)
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"error": "No se pudo parsear evaluación", "raw": texto}
