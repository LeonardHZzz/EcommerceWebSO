from typing import Literal

from pydantic import BaseModel


class WebhookPagoPayload(BaseModel):
    """
    Payload genérico
    """
    id_orden: int
    estado: Literal["completado", "cancelado"]
    referencia_pago: str | None = None
