import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.crud.boleto import boleto_crud
from app.models.usuario import RolUsuario, Usuario
from app.schemas.boleto import ValidarBoletoRequest, ValidarBoletoResponse
from app.schemas.orden import BoletoOut
from app.services.qr_service import generar_imagen_qr_png

router = APIRouter(prefix="/boletos", tags=["Boletos"])


@router.get("/mis-boletos", response_model=list[BoletoOut])
def mis_boletos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """todos los boletos del usuario autenticado a traves de todas sus ordenes."""
    return boleto_crud.list_by_usuario(db, current_user.id_usuario)


@router.get("/{id_boleto}/qr.png")
def obtener_qr_boleto(
    id_boleto: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    devuelve la imagen PNG del codigo QR del boleto
    """
    boleto = boleto_crud.get(db, id_boleto)
    if not boleto:
        raise HTTPException(status_code=404, detail="Boleto no encontrado")

    es_dueno = boleto.detalle and boleto.detalle.orden and boleto.detalle.orden.id_usuario == current_user.id_usuario
    if not es_dueno and current_user.rol != RolUsuario.admin:
        raise HTTPException(status_code=403, detail="No puedes ver este boleto")

    png_bytes = generar_imagen_qr_png(boleto.codigo_qr)
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")


@router.post(
    "/validar-ingreso",
    response_model=ValidarBoletoResponse,
    dependencies=[Depends(get_current_admin)],
)
def validar_ingreso(payload: ValidarBoletoRequest, db: Session = Depends(get_db)):
    """
    escaneo del codigo QR 
    """
    valido, mensaje, boleto = boleto_crud.validar_ingreso(db, payload.codigo_qr)
    return ValidarBoletoResponse(
        valido=valido,
        mensaje=mensaje,
        id_boleto=boleto.id_boleto if boleto else None,
    )
