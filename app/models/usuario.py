import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RolUsuario(str, enum.Enum):
    cliente = "cliente"
    admin = "admin"


class Usuario(Base):
    __tablename__ = "Usuario"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    apellido: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario), nullable=False, default=RolUsuario.cliente)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ordenes: Mapped[list["Orden"]] = relationship(back_populates="usuario")
    carrito: Mapped[list["CarritoCompra"]] = relationship(back_populates="usuario")
