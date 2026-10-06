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
    Notificación de la pasarela de pago (Culqi, Niubiz, MercadoPago, Stripe,
    etc.) sobre el resultado de un cobro. Este endpoint NO usa JWT — no tiene
    sentido pedirle un token de usuario a la pasarela — sino que verifica una
    firma HMAC del cuerpo crudo, calculada con un secreto compartido
    (`WEBHOOK_SECRET`) que configuras también en el panel de tu proveedor.

    Body esperado (ajusta el parsing exacto al formato real de tu pasarela;
    esto es el "contrato interno" mínimo, ver app/schemas/webhook.py):
        {"id_orden": 1, "estado": "completado", "referencia_pago": "ch_xxx"}

    Cómo probarlo en local, generando la firma a mano:
        BODY='{"id_orden": 1, "estado": "completado"}'
        SECRET="tu-webhook-secret"
        FIRMA=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')
        curl -X POST http://localhost:8000/api/v1/webhooks/pagos \
             -H "Content-Type: application/json" \
             -H "X-Webhook-Signature: $FIRMA" \
             -d "$BODY"
    """
    raw_body = await request.body()

    if not verify_webhook_signature(raw_body, x_webhook_signature, settings.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Firma de webhook inválida")

    payload = WebhookPagoPayload.model_validate_json(raw_body)

    orden = db.get(Orden, payload.id_orden)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    estado_destino = EstadoPago.completado if payload.estado == "completado" else EstadoPago.cancelado

    # Idempotencia: las pasarelas de pago reintentan el webhook si no reciben
    # un 200 a tiempo (timeout, caída momentánea, etc.). Si la orden YA está
    # en el estado notificado, respondemos 200 sin volver a aplicar el efecto
    # (evita, por ejemplo, "cancelar" dos veces y devolver el cupón dos veces).
    if orden.estado_pago == estado_destino:
        return orden

    try:
        if estado_destino == EstadoPago.completado:
            return confirmar_pago(db, orden)
        return cancelar_orden(db, orden)
    except CompraError:
        raise
