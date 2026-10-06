from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ZonaBase(BaseModel):
    nombre_zona: str
    precio: Decimal = Field(ge=0)
    capacidad_total: int = Field(gt=0)


class ZonaCreate(ZonaBase):
    """capacidad_disponible se inicializa igual a capacidad_total al crear."""
    pass


class ZonaUpdate(BaseModel):
    nombre_zona: str | None = None
    precio: Decimal | None = Field(default=None, ge=0)
    capacidad_total: int | None = Field(default=None, gt=0)


class ZonaOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id_zona: int
    id_evento: int
    nombre_zona: str
    precio: Decimal
    capacidad_total: int
    capacidad_disponible: int