"""
Promueve un usuario ya registrado a rol 'admin'.
"""
import sys

from app.db.session import SessionLocal
from app.models.usuario import RolUsuario, Usuario


def promote(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if not user:
            print(f"No existe ningún usuario registrado con el email: {email}")
            return
        if user.rol == RolUsuario.admin:
            print(f"{email} ya es admin.")
            return
        user.rol = RolUsuario.admin
        db.add(user)
        db.commit()
        print(f"Listo: {email} ahora tiene rol admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m app.scripts.create_admin <email>")
        sys.exit(1)
    promote(sys.argv[1])
