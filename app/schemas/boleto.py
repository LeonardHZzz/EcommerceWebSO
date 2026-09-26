from pydantic import BaseModel


class ValidarBoletoRequest(BaseModel):
    codigo_qr: str


class ValidarBoletoResponse(BaseModel):
    valido: bool
    mensaje: str
    id_boleto: int | None = None
