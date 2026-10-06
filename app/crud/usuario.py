from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate]):
    def get_by_email(self, db: Session, email: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, db: Session, obj_in: UsuarioCreate) -> Usuario:
        data = obj_in.model_dump()
        raw_password = data.pop("password")
        obj = Usuario(**data, password=hash_password(raw_password))
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update_me(self, db: Session, user: Usuario, data: UsuarioUpdate) -> Usuario:
        update_data = data.model_dump(exclude_unset=True)

        new_email = update_data.get("email")
        if new_email and new_email != user.email:
            existing = self.get_by_email(db, new_email)
            if existing and existing.id_usuario != user.id_usuario:
                raise ValueError("Ese email ya está en uso por otra cuenta")

        raw_password = update_data.pop("password", None)
        for field, value in update_data.items():
            setattr(user, field, value)
        if raw_password:
            user.password = hash_password(raw_password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, email: str, password: str) -> Usuario | None:
        user = self.get_by_email(db, email)
        if not user or not verify_password(password, user.password):
            return None
        return user


usuario_crud = CRUDUsuario(Usuario)
