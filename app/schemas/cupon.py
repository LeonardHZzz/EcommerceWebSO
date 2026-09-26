from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cupon_descuento import EstadoCupon


class CuponBase(BaseModel):
    codigo: str
    porcentaje_descuento: Decimal = Field(gt=0, le=100)
    fecha_vencimiento: datetime
    usos_disponibles: int = Field(ge=0)


class CuponCreate(CuponBase):
    pass


class CuponUpdate(BaseModel):
    porcentaje_descuento: Decimal | None = Field(default=None, gt=0, le=100)
    fecha_vencimiento: datetime | None = None
    usos_disponibles: int | None = Field(default=None, ge=0)
    estado: EstadoCupon | None = None


class CuponOut(CuponBase):
    model_config = ConfigDict(from_attributes=True)

    id_cupon: int
    estado: EstadoCupon


class CuponValidarRequest(BaseModel):
    codigo: str


class CuponValidarResponse(BaseModel):
    valido: bool
    porcentaje_descuento: Decimal | None = None
    mensaje: str
