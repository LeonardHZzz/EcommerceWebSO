from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.zona import zona_crud
from app.schemas.zona import ZonaOut

router = APIRouter(prefix="/zonas", tags=["Zonas"])


@router.get("/{id_zona}", response_model=ZonaOut)
def obtener_zona(id_zona: int, db: Session = Depends(get_db)):
    """
    Consulta puntual de una zona (precio y disponibilidad en tiempo real).
    Útil para que el frontend valide stock justo antes de agregar al carrito.
    """
    zona = zona_crud.get(db, id_zona)
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zona
