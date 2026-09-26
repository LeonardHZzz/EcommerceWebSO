from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.evento import Evento
from app.schemas.evento import EventoCreate


class CRUDEvento(CRUDBase[Evento, EventoCreate]):
    def list_with_zonas(self, db: Session, skip: int = 0, limit: int = 100) -> list[Evento]:
        return (
            db.query(Evento)
            .options(joinedload(Evento.zonas))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_zonas(self, db: Session, id_evento: int) -> Evento | None:
        return (
            db.query(Evento)
            .options(joinedload(Evento.zonas))
            .filter(Evento.id_evento == id_evento)
            .first()
        )


evento_crud = CRUDEvento(Evento)
