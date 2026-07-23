from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConsultaRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=2000)


class ConsultaResponse(BaseModel):
    pregunta: str
    respuesta: str
    agentes_participantes: list[str] = []
    fuentes: list[dict] = []
    identificador: Optional[str] = None


class SolicitudResponse(BaseModel):
    identificador: str
    tipo_contrato: str
    proveedor: str
    objeto: str
    plazo: str
    monto: str
    trata_datos: bool
    fecha_creacion: datetime
