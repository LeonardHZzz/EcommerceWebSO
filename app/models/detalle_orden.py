from decimal import Decimal

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DetalleOrden(Base):
    __tablename__ = "Detalle_orden"

    id_detalle: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_orden: Mapped[int] = mapped_column(ForeignKey("Orden.id_orden"), nullable=False)
    id_zona: Mapped[int] = mapped_column(ForeignKey("Zona.id_zona"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    orden: Mapped["Orden"] = relationship(back_populates="detalles")
    zona: Mapped["Zona"] = relationship(back_populates="detalles_orden")
    boletos: Mapped[list["Boleto"]] = relationship(back_populates="detalle", cascade="all, delete-orphan")
