from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import verify_webhook_signature
from app.models.orden import EstadoPago, Orden
from app.schemas.orden import OrdenOut
from app.schemas.webhook import WebhookPagoPayload
from app.services.compra_service import CompraError, cancelar_orden, confirmar_pago

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/pagos", response_model=OrdenOut)
async def webhook_pago(
    request: Request,
    db: Session = Depends(get_db),
    x_webhook_signature: str = Header(..., alias="X-Webhook-Signature"),
):
    """
    Notificación de la pasarela de pago
    """
    raw_body = await request.body()

    if not verify_webhook_signature(raw_body, x_webhook_signature, settings.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Firma de webhook inválida")

    payload = WebhookPagoPayload.model_validate_json(raw_body)

    orden = db.get(Orden, payload.id_orden)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    estado_destino = EstadoPago.completado if payload.estado == "completado" else EstadoPago.cancelado

    if orden.estado_pago == estado_destino:
        return orden

    try:
        if estado_destino == EstadoPago.completado:
            return confirmar_pago(db, orden)
        return cancelar_orden(db, orden)
    except CompraError:
        raise
