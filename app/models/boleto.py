import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EstadoIngreso(str, enum.Enum):
    valido = "valido"
    usado = "usado"
    anulado = "anulado"


class Boleto(Base):
    __tablename__ = "Boleto"

    id_boleto: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_detalle: Mapped[int] = mapped_column(ForeignKey("Detalle_orden.id_detalle"), nullable=False)
    codigo_qr: Mapped[str] = mapped_column(String(191), unique=True, nullable=False, index=True)
    estado_ingreso: Mapped[EstadoIngreso] = mapped_column(
        Enum(EstadoIngreso), nullable=False, default=EstadoIngreso.valido
    )
    fecha_ingreso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    detalle: Mapped["DetalleOrden"] = relationship(back_populates="boletos")
