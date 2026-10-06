from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.crud.evento import evento_crud
from app.crud.zona import zona_crud
from app.models.evento import Evento
from app.schemas.evento import EventoCreate, EventoOut, EventoUpdate
from app.schemas.zona import ZonaCreate, ZonaOut, ZonaUpdate

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ---- Catálogo público ----

@router.get("", response_model=list[EventoOut])
def listar_eventos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Catálogo público de eventos (ej. Sugoi Fest 2027), con sus zonas y precios."""
    return evento_crud.list_with_zonas(db, skip=skip, limit=limit)


@router.get("/{id_evento}", response_model=EventoOut)
def obtener_evento(id_evento: int, db: Session = Depends(get_db)):
    evento = evento_crud.get_with_zonas(db, id_evento)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento


# ---- Administración (solo admin) ----

@router.post("", response_model=EventoOut, status_code=201, dependencies=[Depends(get_current_admin)])
def crear_evento(payload: EventoCreate, db: Session = Depends(get_db)):
    return evento_crud.create(db, payload)


@router.put("/{id_evento}", response_model=EventoOut, dependencies=[Depends(get_current_admin)])
def actualizar_evento(id_evento: int, payload: EventoUpdate, db: Session = Depends(get_db)):
    evento = evento_crud.get(db, id_evento)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(evento, field, value)
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


@router.delete("/{id_evento}", status_code=204, dependencies=[Depends(get_current_admin)])
def eliminar_evento(id_evento: int, db: Session = Depends(get_db)):
    evento = evento_crud.get(db, id_evento)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    evento_crud.delete(db, id_evento)


# ---- Zonas de un evento (anidado bajo /eventos, admin) ----

@router.post(
    "/{id_evento}/zonas",
    response_model=ZonaOut,
    status_code=201,
    dependencies=[Depends(get_current_admin)],
)
def crear_zona(id_evento: int, payload: ZonaCreate, db: Session = Depends(get_db)):
    evento = db.get(Evento, id_evento)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return zona_crud.create(db, id_evento, payload)


@router.put(
    "/{id_evento}/zonas/{id_zona}",
    response_model=ZonaOut,
    dependencies=[Depends(get_current_admin)],
)
def actualizar_zona(id_evento: int, id_zona: int, payload: ZonaUpdate, db: Session = Depends(get_db)):
    zona = zona_crud.get(db, id_zona)
    if not zona or zona.id_evento != id_evento:
        raise HTTPException(status_code=404, detail="Zona no encontrada para este evento")
    return zona_crud.update(db, zona, payload)


@router.delete(
    "/{id_evento}/zonas/{id_zona}",
    status_code=204,
    dependencies=[Depends(get_current_admin)],
)
def eliminar_zona(id_evento: int, id_zona: int, db: Session = Depends(get_db)):
    zona = zona_crud.get(db, id_zona)
    if not zona or zona.id_evento != id_evento:
        raise HTTPException(status_code=404, detail="Zona no encontrada para este evento")
    zona_crud.delete(db, zona)
