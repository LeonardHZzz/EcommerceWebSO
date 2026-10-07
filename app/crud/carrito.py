from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.carrito import carrito_crud
from app.models.usuario import Usuario
from app.schemas.carrito import CarritoItemCreate, CarritoItemOut, CarritoItemUpdate

router = APIRouter(prefix="/carrito", tags=["Carrito"])


@router.get("", response_model=list[CarritoItemOut])
def ver_carrito(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return carrito_crud.list_by_usuario(db, current_user.id_usuario)


@router.post("", response_model=CarritoItemOut, status_code=201)
def agregar_al_carrito(
    payload: CarritoItemCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return carrito_crud.add_item(db, current_user.id_usuario, payload.id_zona, payload.cantidad)


@router.patch("/{id_carrito}", response_model=CarritoItemOut)
def actualizar_cantidad(
    id_carrito: int,
    payload: CarritoItemUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = carrito_crud.update_cantidad(db, current_user.id_usuario, id_carrito, payload.cantidad)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem de carrito no encontrado")
    return item


@router.delete("/{id_carrito}", status_code=204)
def quitar_del_carrito(
    id_carrito: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    carrito_crud.remove_item(db, current_user.id_usuario, id_carrito)
