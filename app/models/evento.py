import enum
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EstadoEvento(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    finalizado = "finalizado"


class Evento(Base):
    __tablename__ = "Evento"

    id_evento: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_categoria: Mapped[int] = mapped_column(ForeignKey("Categoria.id_categoria"), nullable=False)
    id_recinto: Mapped[int] = mapped_column(ForeignKey("Recinto.id_recinto"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[EstadoEvento] = mapped_column(Enum(EstadoEvento), nullable=False, default=EstadoEvento.activo)

    categoria: Mapped["Categoria"] = relationship(back_populates="eventos")
    recinto: Mapped["Recinto"] = relationship(back_populates="eventos")
    zonas: Mapped[list["Zona"]] = relationship(back_populates="evento", cascade="all, delete-orphan")
