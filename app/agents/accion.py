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
    """Registra una solicitud de elaboración o revisión de contrato.

    Requiere: tipo_contrato, proveedor, objeto, plazo, monto,
    trata_datos_personales (sí/no).
    Si falta algún dato, NO registra y devuelve cuáles faltan.
    Si datos están completos pero confirmado=False, pide confirmación.
    Solo escribe en BD cuando confirmado=True.
    """
    datos = {
        "tipo_contrato": tipo_contrato,
        "proveedor": proveedor,
        "objeto": objeto,
        "plazo": plazo,
        "monto": monto,
        "trata_datos_personales": trata_datos_personales,
    }

    faltantes = [k for k in CAMPOS_SOLICITUD if not str(datos[k]).strip()]
    if faltantes:
        return (
            "No se registró. Faltan datos obligatorios: "
            f"{', '.join(faltantes)}."
        )

    if not confirmado:
        resumen = (
            f"Tipo: {tipo_contrato} | Proveedor: {proveedor} | "
            f"Objeto: {objeto} | Plazo: {plazo} | "
            f"Monto: {monto} | Trata datos: {trata_datos_personales}"
        )
        return (
            f"CONFIRMACIÓN REQUERIDA. Estos son los datos:\n"
            f"{resumen}\n"
            "Responde 'sí' para confirmar el registro."
        )

    rid = _siguiente_id_solicitud()
    with Session(sync_engine) as session:
        solicitud = SolicitudLegal(
            identificador=rid,
            tipo_contrato=tipo_contrato,
            proveedor=proveedor,
            objeto=objeto,
            plazo=plazo,
            monto=monto,
            trata_datos=trata_datos_personales.lower()
            in ("sí", "si", "yes", "true"),
            fecha_creacion=datetime.now(),
        )
        session.add(solicitud)
        session.commit()

    return f"Solicitud registrada con ID {rid}."
