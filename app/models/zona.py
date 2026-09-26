from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Zona(Base):
    __tablename__ = "Zona"

    id_zona: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_evento: Mapped[int] = mapped_column(ForeignKey("Evento.id_evento"), nullable=False)
    nombre_zona: Mapped[str] = mapped_column(String(50), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    capacidad_total: Mapped[int] = mapped_column(Integer, nullable=False)
    capacidad_disponible: Mapped[int] = mapped_column(Integer, nullable=False)

    evento: Mapped["Evento"] = relationship(back_populates="zonas")
    detalles_orden: Mapped[list["DetalleOrden"]] = relationship(back_populates="zona")
    carrito_items: Mapped[list["CarritoCompra"]] = relationship(back_populates="zona")
