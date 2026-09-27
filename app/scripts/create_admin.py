"""
Promueve un usuario ya registrado a rol 'admin'.

No existe (a propósito) un endpoint público para esto: crear admins debe
ser una acción manual de quien opera el sistema, no algo alcanzable desde
la API por cualquier usuario registrado.

Uso (con el stack local corriendo):
    docker compose -f docker-compose.local.yml exec api python -m app.scripts.create_admin correo@ejemplo.com

Uso en la VM de Azure (dentro del contenedor o del venv):
    python -m app.scripts.create_admin correo@ejemplo.com
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
