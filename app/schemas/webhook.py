from typing import Literal

from pydantic import BaseModel


class WebhookPagoPayload(BaseModel):
    """
    Payload genérico esperado del webhook de la pasarela de pago.

    Cada pasarela real (Culqi, Niubiz, MercadoPago, Stripe...) tiene su
    propio formato de evento; adapta el parsing en el endpoint del webhook
    al de tu proveedor específico, manteniendo esta forma como el
    "contrato interno" mínimo que necesita tu Orden.
    """
    id_orden: int
    estado: Literal["completado", "cancelado"]
    referencia_pago: str | None = None
