from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.evento import EstadoEvento
from app.schemas.zona import ZonaOut


class EventoBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    id_categoria: int
    id_recinto: int
    fecha_inicio: datetime
    fecha_fin: datetime


class EventoCreate(EventoBase):
    pass


class EventoUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    id_categoria: int | None = None
    id_recinto: int | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    estado: EstadoEvento | None = None


class EventoOut(EventoBase):
    model_config = ConfigDict(from_attributes=True)

    id_evento: int
    estado: EstadoEvento
    zonas: list[ZonaOut] = []
