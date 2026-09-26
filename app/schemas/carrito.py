from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CarritoItemCreate(BaseModel):
    id_zona: int
    cantidad: int = Field(gt=0)


class CarritoItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_carrito: int
    id_zona: int
    cantidad: int
    fecha_agregado: datetime
