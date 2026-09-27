from datetime import datetime, timedelta, timezone
from typing import Any
import hashlib
import hmac

import bcrypt
from jose import jwt

from app.core.config import settings

# bcrypt trunca (por especificación del algoritmo) todo lo que exceda 72 bytes;
# lo hacemos explícito aquí para no depender del comportamiento interno de la
# librería ante contraseñas inusualmente largas.
_MAX_BCRYPT_BYTES = 72


def _prepare(password: str) -> bytes:
    return password.encode("utf-8")[:_MAX_BCRYPT_BYTES]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_prepare(plain_password), hashed_password.encode("utf-8"))


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """
    Verifica la firma HMAC-SHA256 de un webhook entrante (patrón usado por
    Culqi, Niubiz, MercadoPago, Stripe, etc.): la pasarela firma el cuerpo
    crudo de la petición con un secreto compartido, y nosotros recalculamos
    la misma firma para confirmar que el request realmente vino de ella
    (y no de alguien falseando un "pago completado").

    `hmac.compare_digest` evita timing attacks al comparar (una comparación
    ingenua con `==` filtra información por cuánto tiempo tarda en fallar).
    """
    if not secret or not signature:
        return False
    firma_esperada = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(firma_esperada, signature)
