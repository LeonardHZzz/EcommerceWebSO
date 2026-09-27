import io
import uuid

import qrcode


def generar_codigo_qr(id_orden: int, id_detalle: int, indice: int) -> str:
    """
    Genera un código único para el boleto. Aquí solo se genera el string
    que se guarda en `codigo_qr`; el render de la imagen QR (con la
    librería `qrcode`) se hace en el endpoint que sirve/descarga el boleto,
    no al momento de crearlo (evita guardar binarios pesados en BD).
    """
    return f"ORD{id_orden}-DET{id_detalle}-{indice}-{uuid.uuid4().hex[:8].upper()}"


def generar_imagen_qr_png(codigo_qr: str) -> bytes:
    """
    Renderiza el código como imagen PNG lista para mostrar o imprimir.
    Se genera bajo demanda (no se guarda en BD ni en disco): es barato de
    calcular y evita tener binarios pesados fuera de sincronía con el código.
    """
    img = qrcode.make(codigo_qr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
