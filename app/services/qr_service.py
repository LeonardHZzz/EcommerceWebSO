import io
import uuid
import qrcode


def generar_codigo_qr(id_orden: int, id_detalle: int, indice: int) -> str:
    """
    Genera un codigo unico para el boleto
    """
    return f"ORD{id_orden}-DET{id_detalle}-{indice}-{uuid.uuid4().hex[:8].upper()}"


def generar_imagen_qr_png(codigo_qr: str) -> bytes:
    """
    Renderiza el codigo como imagen PNG
    """
    img = qrcode.make(codigo_qr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
