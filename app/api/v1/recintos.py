from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.crud.recinto import recinto_crud
from app.schemas.recinto import RecintoCreate, RecintoOut, RecintoUpdate

router = APIRouter(prefix="/recintos", tags=["Recintos"])


@router.get("", response_model=list[RecintoOut])
def listar_recintos(db: Session = Depends(get_db)):
    return recinto_crud.list(db, limit=200)


@router.get("/{id_recinto}", response_model=RecintoOut)
def obtener_recinto(id_recinto: int, db: Session = Depends(get_db)):
    obj = recinto_crud.get(db, id_recinto)
    if not obj:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    return obj


@router.post("", response_model=RecintoOut, status_code=201, dependencies=[Depends(get_current_admin)])
def crear_recinto(payload: RecintoCreate, db: Session = Depends(get_db)):
    return recinto_crud.create(db, payload)


@router.put("/{id_recinto}", response_model=RecintoOut, dependencies=[Depends(get_current_admin)])
def actualizar_recinto(id_recinto: int, payload: RecintoUpdate, db: Session = Depends(get_db)):
    obj = recinto_crud.get(db, id_recinto)
    if not obj:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id_recinto}", status_code=204, dependencies=[Depends(get_current_admin)])
def eliminar_recinto(id_recinto: int, db: Session = Depends(get_db)):
    obj = recinto_crud.get(db, id_recinto)
    if not obj:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    recinto_crud.delete(db, id_recinto)
