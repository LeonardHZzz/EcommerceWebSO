from typing import Generic, TypeVar, Type, Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    """CRUD generico"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id_: int) -> ModelType | None:
        return db.get(self.model, id_)

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, id_: int, obj_in: BaseModel) -> ModelType | None:
        obj = self.get(db, id_)
        if obj is None:
            return None
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id_: int) -> ModelType | None:
        obj = self.get(db, id_)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
