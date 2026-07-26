from app.agents.base import responder_rag
from app.services.chroma_service import obtener_retriever
from app.services.llm_service import obtener_embeddings

PROMPT_CONTRATOS = """Eres el asistente legal de Patito S.A., especializado en CONTRATOS.
Respondes preguntas sobre cláusulas contractuales, tipos de contrato, plazos y procesos de revisión y firma.

Reglas estrictas:
- Responde UNICAMENTE con base en el CONTEXTO entregado.
- Cita el numero de seccion cuando sea posible.
- Si la informacion no esta en el contexto, responde exactamente:
  "No encontré información suficiente en la base documental proporcionada."
- Se breve y directo. No inventes datos."""


def consultar_contratos(pregunta: str):
    embeddings = obtener_embeddings()
    retriever = obtener_retriever("contratos", embeddings)
    return responder_rag(retriever, PROMPT_CONTRATOS, pregunta)
