import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    completado = "completado"
    cancelado = "cancelado"


class Orden(Base):
    __tablename__ = "Orden"

    id_orden: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("Usuario.id_usuario"), nullable=False)
    id_cupon: Mapped[int | None] = mapped_column(ForeignKey("CuponesDescuento.id_cupon"), nullable=True)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado_pago: Mapped[EstadoPago] = mapped_column(Enum(EstadoPago), nullable=False, default=EstadoPago.pendiente)
    metodo_pago: Mapped[str | None] = mapped_column(String(50))
    fecha_compra: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="ordenes")
    cupon: Mapped["CuponDescuento"] = relationship(back_populates="ordenes")
    detalles: Mapped[list["DetalleOrden"]] = relationship(back_populates="orden", cascade="all, delete-orphan")
