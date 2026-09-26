from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CarritoCompra(Base):
    __tablename__ = "CarritoCompra"

    id_carrito: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("Usuario.id_usuario"), nullable=False)
    id_zona: Mapped[int] = mapped_column(ForeignKey("Zona.id_zona"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_agregado: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="carrito")
    zona: Mapped["Zona"] = relationship(back_populates="carrito_items")
