import base64

from langchain_core.messages import HumanMessage

from app.services.llm_service import obtener_llm


def analizar_documento_legal(ruta_imagen: str) -> str:
    try:
        with open(ruta_imagen, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return f"No se encontró la imagen '{ruta_imagen}'."

    prompt = (
        "Analiza esta imagen de un documento legal (contrato, identificación o formulario). "
        "Extrae y devuelve en lineas separadas: tipo de documento, "
        "partes intervinientes, objeto, plazo, monto, cláusulas visibles, firmas y sellos. "
        "Indica si el documento es legible y si detectas alguna cláusula faltante. "
        "Si algún dato no aparece, escribe 'no visible'."
    )
    msg = HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": f"data:image/png;base64,{b64}"},
    ])
    llm = obtener_llm()
    return llm.invoke([msg]).content
