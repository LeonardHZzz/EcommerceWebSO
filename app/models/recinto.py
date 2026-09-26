from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recinto(Base):
    __tablename__ = "Recinto"

    id_recinto: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_recinto: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(String(150), nullable=False)
    distrito: Mapped[str | None] = mapped_column(String(50))
    aforo_maximo: Mapped[int] = mapped_column(Integer, nullable=False)

    eventos: Mapped[list["Evento"]] = relationship(back_populates="recinto")
