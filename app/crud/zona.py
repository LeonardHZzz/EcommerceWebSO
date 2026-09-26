from sqlalchemy.orm import Session

from app.models.zona import Zona
from app.schemas.zona import ZonaCreate, ZonaUpdate


class CRUDZona:
    def get(self, db: Session, id_zona: int) -> Zona | None:
        return db.get(Zona, id_zona)

    def list_by_evento(self, db: Session, id_evento: int) -> list[Zona]:
        return db.query(Zona).filter(Zona.id_evento == id_evento).all()

    def create(self, db: Session, id_evento: int, obj_in: ZonaCreate) -> Zona:
        zona = Zona(
            id_evento=id_evento,
            nombre_zona=obj_in.nombre_zona,
            precio=obj_in.precio,
            capacidad_total=obj_in.capacidad_total,
            capacidad_disponible=obj_in.capacidad_total,  
        )
        db.add(zona)
        db.commit()
        db.refresh(zona)
        return zona

    def update(self, db: Session, zona: Zona, obj_in: ZonaUpdate) -> Zona:
        data = obj_in.model_dump(exclude_unset=True)
        if "capacidad_total" in data:
            diferencia = data["capacidad_total"] - zona.capacidad_total
            zona.capacidad_disponible = max(0, zona.capacidad_disponible + diferencia)
        for field, value in data.items():
            setattr(zona, field, value)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        return zona

    def delete(self, db: Session, zona: Zona) -> None:
        db.delete(zona)
        db.commit()


zona_crud = CRUDZona()