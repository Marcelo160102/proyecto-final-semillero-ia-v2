from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.config import obtener_config
from app.db.models import Base, SolicitudLegal

config = obtener_config()

sync_engine = create_engine(config.database_url.replace("+aiosqlite", ""))
Base.metadata.create_all(sync_engine)

CAMPOS_SOLICITUD = [
    "tipo_contrato", "proveedor", "objeto", "plazo",
    "monto", "trata_datos_personales",
]

_pendiente: dict | None = None


def _siguiente_id_solicitud() -> str:
    with Session(sync_engine) as session:
        count = session.query(SolicitudLegal).count()
        return f"LEG-{count + 1:04d}"


def registrar_solicitud_legal(
    tipo_contrato: str = "",
    proveedor: str = "",
    objeto: str = "",
    plazo: str = "",
    monto: str = "",
    trata_datos_personales: str = "",
    confirmado: bool = False,
) -> str:
    """Registra una solicitud de elaboracion o revision de contrato.

    Requiere: tipo_contrato, proveedor, objeto, plazo, monto,
    trata_datos_personales (si/no).
    Si falta algun dato, NO registra y devuelve cuales faltan.
    Si datos estan completos pero confirmado=False, pide confirmacion.
    Si confirmado=True y algunos datos estan vacios, el sistema reutiliza
    los datos de la llamada anterior.
    Solo escribe en BD cuando confirmado=True.
    """
    global _pendiente

    datos = {
        "tipo_contrato": tipo_contrato,
        "proveedor": proveedor,
        "objeto": objeto,
        "plazo": plazo,
        "monto": monto,
        "trata_datos_personales": trata_datos_personales,
    }

    faltantes = [k for k in CAMPOS_SOLICITUD if not str(datos[k]).strip()]

    if faltantes and confirmado and _pendiente is not None:
        datos = _pendiente
        faltantes = []

    if faltantes:
        return (
            "No se registro. Faltan datos obligatorios: "
            f"{', '.join(faltantes)}."
        )

    if not confirmado:
        _pendiente = datos
        resumen = (
            f"Tipo: {datos['tipo_contrato']} | Proveedor: {datos['proveedor']} | "
            f"Objeto: {datos['objeto']} | Plazo: {datos['plazo']} | "
            f"Monto: {datos['monto']} | Trata datos: {datos['trata_datos_personales']}"
        )
        return (
            f"CONFIRMACION REQUERIDA. Estos son los datos:\n"
            f"{resumen}\n"
            "Responde 'si' para confirmar el registro."
        )

    d = datos
    rid = _siguiente_id_solicitud()
    with Session(sync_engine) as session:
        solicitud = SolicitudLegal(
            identificador=rid,
            tipo_contrato=d["tipo_contrato"],
            proveedor=d["proveedor"],
            objeto=d["objeto"],
            plazo=d["plazo"],
            monto=d["monto"],
            trata_datos=d["trata_datos_personales"].lower()
            in ("si", "sí", "yes", "true"),
            fecha_creacion=datetime.now(),
        )
        session.add(solicitud)
        session.commit()

    _pendiente = None
    return f"Solicitud registrada con ID {rid}."
