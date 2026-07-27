from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SolicitudLegal(Base):
    __tablename__ = "solicitudes_legales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identificador: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    tipo_contrato: Mapped[str] = mapped_column(String(100), nullable=False)
    proveedor: Mapped[str] = mapped_column(String(200), nullable=False)
    objeto: Mapped[str] = mapped_column(String(500), nullable=False)
    plazo: Mapped[str] = mapped_column(String(100), nullable=False)
    monto: Mapped[str] = mapped_column(String(50), nullable=False)
    trata_datos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pregunta: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta: Mapped[str] = mapped_column(Text, nullable=False)
    agentes_participantes: Mapped[str] = mapped_column(Text, nullable=True)
    fuentes: Mapped[str] = mapped_column(Text, nullable=True)
    evaluacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
