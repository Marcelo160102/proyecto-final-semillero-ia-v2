import logging

from app.services.llm_service import obtener_llm


def extraer_texto(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for b in content:
            if isinstance(b, dict):
                partes.append(b.get("text", ""))
            elif isinstance(b, str):
                partes.append(b)
        return "".join(partes).strip()
    return str(content)


def responder_rag(retriever, prompt_sistema, pregunta):
    llm = obtener_llm()
    try:
        docs = retriever.invoke(pregunta)
    except Exception as e:
        logging.error("Error al recuperar documentos de ChromaDB: %s", e)
        return "No se pudo acceder a la base de conocimiento. Intente mas tarde.", []
    contexto = "\n\n---\n\n".join(d.page_content for d in docs)
    try:
        msg = llm.invoke([
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"},
        ])
    except Exception as e:
        logging.error("Error al invocar Gemini: %s", e)
        return "El servicio de Gemini no esta disponible en este momento. Intente mas tarde.", docs
    respuesta = extraer_texto(msg.content)
    return respuesta, docs
