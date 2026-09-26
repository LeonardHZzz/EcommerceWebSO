import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EstadoCupon(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class CuponDescuento(Base):
    __tablename__ = "CuponesDescuento"

    id_cupon: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    porcentaje_descuento: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usos_disponibles: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[EstadoCupon] = mapped_column(Enum(EstadoCupon), nullable=False, default=EstadoCupon.activo)

    ordenes: Mapped[list["Orden"]] = relationship(back_populates="cupon")
