from app.agents.base import responder_rag
from app.services.chroma_service import obtener_retriever
from app.services.llm_service import obtener_embeddings

PROMPT_DATOS = """Eres el asistente legal de Patito S.A., especializado en PROTECCION DE DATOS PERSONALES.
Respondes preguntas sobre tratamiento de datos, consentimiento, derechos ARCO, retención y seguridad.

Reglas estrictas:
- Responde UNICAMENTE con base en el CONTEXTO entregado.
- Cita el numero de seccion cuando sea posible.
- Si la informacion no esta en el contexto, responde exactamente:
  "No tengo esa informacion en la base documental proporcionada."
- Se breve y directo. No inventes datos."""


def consultar_proteccion_datos(pregunta: str):
    embeddings = obtener_embeddings()
    retriever = obtener_retriever("proteccion_datos", embeddings)
    return responder_rag(retriever, PROMPT_DATOS, pregunta)
