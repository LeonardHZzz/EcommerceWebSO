from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.orden import EstadoPago
from app.models.boleto import EstadoIngreso


class CheckoutRequest(BaseModel):
    """usuario carrito"""
    codigo_cupon: str | None = None
    metodo_pago: str


class BoletoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_boleto: int
    codigo_qr: str
    estado_ingreso: EstadoIngreso
    fecha_ingreso: datetime | None = None


class DetalleOrdenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle: int
    id_zona: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    boletos: list[BoletoOut] = []


class OrdenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_orden: int
    id_usuario: int
    monto_total: Decimal
    estado_pago: EstadoPago
    metodo_pago: str | None
    fecha_compra: datetime
    detalles: list[DetalleOrdenOut] = []
