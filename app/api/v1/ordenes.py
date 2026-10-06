from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.orden import Orden
from app.models.usuario import Usuario
from app.schemas.orden import CheckoutRequest, OrdenOut
from app.services.compra_service import (
    CompraError,
    cancelar_orden,
    confirmar_pago,
    procesar_checkout,
)

router = APIRouter(prefix="/ordenes", tags=["Ordenes"])


def _get_orden_o_404(db: Session, id_orden: int) -> Orden:
    orden = db.get(Orden, id_orden)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden


@router.post("/checkout", response_model=OrdenOut, status_code=201)
def checkout(
    payload: CheckoutRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirma la compra a partir del carrito actual del usuario (queda en estado 'pendiente')."""
    return procesar_checkout(
        db=db,
        id_usuario=current_user.id_usuario,
        metodo_pago=payload.metodo_pago,
        codigo_cupon=payload.codigo_cupon,
    )


@router.get("", response_model=list[OrdenOut])
def mis_ordenes(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Orden).filter(Orden.id_usuario == current_user.id_usuario).all()


@router.get("/{id_orden}", response_model=OrdenOut)
def obtener_orden(
    id_orden: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orden = _get_orden_o_404(db, id_orden)
    if orden.id_usuario != current_user.id_usuario and current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No puedes ver esta orden")
    return orden


@router.patch("/{id_orden}/cancelar", response_model=OrdenOut)
def cancelar(
    id_orden: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    El dueño de la orden (o un admin) puede cancelarla. Revierte el stock
    de las zonas involucradas y anula los boletos ya generados.
    """
    orden = _get_orden_o_404(db, id_orden)
    if orden.id_usuario != current_user.id_usuario and current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No puedes cancelar esta orden")
    try:
        return cancelar_orden(db, orden)
    except CompraError:
        raise


# ---- Solo admin: confirmar pago (simula webhook de pasarela) y ver todas las órdenes ----

@router.get("/admin/todas", response_model=list[OrdenOut], dependencies=[Depends(get_current_admin)])
def listar_todas_las_ordenes(db: Session = Depends(get_db)):
    return db.query(Orden).all()


@router.patch(
    "/{id_orden}/confirmar",
    response_model=OrdenOut,
    dependencies=[Depends(get_current_admin)],
)
def confirmar(id_orden: int, db: Session = Depends(get_db)):
    """
    Marca la orden como pagada/completada. En producción esto lo dispara el
    webhook de la pasarela de pago; se deja también accesible a un admin
    para pruebas manuales o conciliación.
    """
    orden = _get_orden_o_404(db, id_orden)
    return confirmar_pago(db, orden)
