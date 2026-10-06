from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.core.security import create_access_token
from app.crud.usuario import usuario_crud
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate, Token

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
    Perfil del usuario autenticado. A propósito NO recibe un id por URL:
    el usuario se identifica por el token JWT (header Authorization),
    nunca por un id que cualquiera podría cambiar en la URL.
    """
    return current_user


@router.patch("/me", response_model=UsuarioOut)
def actualizar_perfil(
    payload: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edita el perfil del propio usuario autenticado. Igual que /me (GET),
    nunca recibe un id por URL: siempre opera sobre el dueño del token.
    Todos los campos son opcionales — solo se cambia lo que se envía.
    """
    try:
        return usuario_crud.update_me(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id_usuario}", response_model=UsuarioOut, dependencies=[Depends(get_current_admin)])
def obtener_usuario_por_id(id_usuario: int, db: Session = Depends(get_db)):
    """
    Consulta cualquier usuario por su ID. A diferencia de /me, este sí
    recibe el id por URL — pero por eso mismo solo un admin puede usarlo
    (si no, cualquiera podría ver los datos de cualquier otro usuario
    con solo cambiar el número en la URL).
    """
    user = usuario_crud.get(db, id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
