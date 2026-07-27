from langchain.tools import tool

from app.agents.accion import registrar_solicitud_legal
from app.agents.base import extraer_texto
from app.agents.contratos import consultar_contratos as rag_contratos
from app.agents.cumplimiento import consultar_cumplimiento as rag_cumplimiento
from app.agents.multimodal import analizar_documento_legal
from app.agents.proteccion_datos import consultar_proteccion_datos as rag_datos


@tool
def consultar_contratos(pregunta: str) -> str:
    """Responde preguntas sobre contratos: cláusulas mínimas, tipos de contrato, plazos, proceso de revisión y firma. Usa la base de conocimiento de cláusulas contractuales."""
    respuesta, docs = rag_contratos(pregunta)
    fuentes = "; ".join(
        f"sección {d.metadata.get('seccion', '?')}" for d in docs
    )
    return f"{respuesta}\n[Fuentes: {fuentes}]"


@tool
def consultar_proteccion_datos(pregunta: str) -> str:
    """Responde preguntas sobre protección de datos personales: derechos ARCO, retención, seguridad, brechas. Usa la base de conocimiento de protección de datos."""
    respuesta, docs = rag_datos(pregunta)
    fuentes = "; ".join(
        f"sección {d.metadata.get('seccion', '?')}" for d in docs
    )
    return f"{respuesta}\n[Fuentes: {fuentes}]"


@tool
def consultar_cumplimiento(pregunta: str) -> str:
    """Responde preguntas sobre cumplimiento normativo: código de ética, conflictos de interés, regalos, anticorrupción, canal de denuncias. Usa la base de conocimiento de cumplimiento."""
    respuesta, docs = rag_cumplimiento(pregunta)
    fuentes = "; ".join(
        f"sección {d.metadata.get('seccion', '?')}" for d in docs
    )
    return f"{respuesta}\n[Fuentes: {fuentes}]"


@tool
def analizar_documento_legal_tool(ruta_imagen: str) -> str:
    """Analiza la imagen de un documento legal (contrato, identificación o formulario) y extrae tipo, partes, cláusulas, firmas y sellos. Recibe la RUTA del archivo de imagen."""
    return analizar_documento_legal(ruta_imagen)


@tool
def registrar_solicitud_legal_tool(
    tipo_contrato: str = "",
    proveedor: str = "",
    objeto: str = "",
    plazo: str = "",
    monto: str = "",
    trata_datos_personales: str = "",
    confirmado: bool = False,
) -> str:
    """Registra una solicitud de elaboracion o revision de contrato. Requiere: tipo_contrato, proveedor, objeto, plazo, monto, trata_datos_personales. Si falta algun dato, devuelve cuales faltan. Si datos estan completos pero confirmado=False, pide confirmacion. Si confirmado=True y algunos datos estan vacios, el sistema reutiliza los datos de la llamada anterior."""
    return registrar_solicitud_legal(
        tipo_contrato=tipo_contrato,
        proveedor=proveedor,
        objeto=objeto,
        plazo=plazo,
        monto=monto,
        trata_datos_personales=trata_datos_personales,
        confirmado=confirmado,
    )


TOOLS_ORQUESTADOR = [
    consultar_contratos,
    consultar_proteccion_datos,
    consultar_cumplimiento,
    analizar_documento_legal_tool,
    registrar_solicitud_legal_tool,
]
