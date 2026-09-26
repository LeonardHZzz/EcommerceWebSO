from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.crud.categoria import categoria_crud
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return categoria_crud.list(db, limit=200)


@router.get("/{id_categoria}", response_model=CategoriaOut)
def obtener_categoria(id_categoria: int, db: Session = Depends(get_db)):
    obj = categoria_crud.get(db, id_categoria)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return obj


@router.post("", response_model=CategoriaOut, status_code=201, dependencies=[Depends(get_current_admin)])
def crear_categoria(payload: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_crud.create(db, payload)


@router.put("/{id_categoria}", response_model=CategoriaOut, dependencies=[Depends(get_current_admin)])
def actualizar_categoria(id_categoria: int, payload: CategoriaUpdate, db: Session = Depends(get_db)):
    obj = categoria_crud.get(db, id_categoria)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id_categoria}", status_code=204, dependencies=[Depends(get_current_admin)])
def eliminar_categoria(id_categoria: int, db: Session = Depends(get_db)):
    obj = categoria_crud.get(db, id_categoria)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    categoria_crud.delete(db, id_categoria)
