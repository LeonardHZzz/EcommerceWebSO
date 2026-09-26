from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.crud.cupon import cupon_crud
from app.schemas.cupon import (
    CuponCreate,
    CuponOut,
    CuponUpdate,
    CuponValidarRequest,
    CuponValidarResponse,
)

router = APIRouter(prefix="/cupones", tags=["Cupones"])


@router.post("/validar", response_model=CuponValidarResponse)
def validar_cupon(
    payload: CuponValidarRequest,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user), 
):
    """
    Valida un cupón SIN consumir
    """
    valido, mensaje, cupon = cupon_crud.validar(db, payload.codigo)
    return CuponValidarResponse(
        valido=valido,
        porcentaje_descuento=cupon.porcentaje_descuento if cupon else None,
        mensaje=mensaje,
    )

@router.get("", response_model=list[CuponOut], dependencies=[Depends(get_current_admin)])
def listar_cupones(db: Session = Depends(get_db)):
    return cupon_crud.list(db, limit=200)


@router.post("", response_model=CuponOut, status_code=201, dependencies=[Depends(get_current_admin)])
def crear_cupon(payload: CuponCreate, db: Session = Depends(get_db)):
    if cupon_crud.get_by_codigo(db, payload.codigo):
        raise HTTPException(status_code=400, detail="Ya existe un cupón con ese código")
    return cupon_crud.create(db, payload)


@router.put("/{id_cupon}", response_model=CuponOut, dependencies=[Depends(get_current_admin)])
def actualizar_cupon(id_cupon: int, payload: CuponUpdate, db: Session = Depends(get_db)):
    cupon = cupon_crud.get(db, id_cupon)
    if not cupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cupon, field, value)
    db.add(cupon)
    db.commit()
    db.refresh(cupon)
    return cupon


@router.delete("/{id_cupon}", status_code=204, dependencies=[Depends(get_current_admin)])
def eliminar_cupon(id_cupon: int, db: Session = Depends(get_db)):
    cupon = cupon_crud.get(db, id_cupon)
    if not cupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    cupon_crud.delete(db, id_cupon)
