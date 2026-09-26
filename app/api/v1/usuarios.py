from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.core.security import create_access_token
from app.crud.usuario import usuario_crud
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    if usuario_crud.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return usuario_crud.create(db, payload)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = usuario_crud.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token(subject=user.id_usuario)
    return Token(access_token=token)


@router.get("/me", response_model=UsuarioOut)
def leer_perfil(current_user: Usuario = Depends(get_current_user)):
    """
    Perfil del usuario autenticado
    """
    return current_user


@router.get("/{id_usuario}", response_model=UsuarioOut, dependencies=[Depends(get_current_admin)])
def obtener_usuario_por_id(id_usuario: int, db: Session = Depends(get_db)):
    """
    Consulta cualquier usuario por su ID
    """
    user = usuario_crud.get(db, id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
