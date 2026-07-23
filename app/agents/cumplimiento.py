from app.agents.base import responder_rag
from app.services.chroma_service import obtener_retriever
from app.services.llm_service import obtener_embeddings

PROMPT_CUMPLIMIENTO = """Eres el asistente legal de Patito S.A., especializado en CUMPLIMIENTO NORMATIVO.
Respondes preguntas sobre código de ética, conflictos de interés, regalos, anticorrupción y denuncias.

Reglas estrictas:
- Responde UNICAMENTE con base en el CONTEXTO entregado.
- Cita el numero de seccion cuando sea posible.
- Si la informacion no esta en el contexto, responde exactamente:
  "No tengo esa informacion en la base documental proporcionada."
- Se breve y directo. No inventes datos."""


def consultar_cumplimiento(pregunta: str):
    embeddings = obtener_embeddings()
    retriever = obtener_retriever("cumplimiento", embeddings)
    return responder_rag(retriever, PROMPT_CUMPLIMIENTO, pregunta)
