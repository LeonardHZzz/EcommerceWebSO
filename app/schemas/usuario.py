from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.usuario import RolUsuario


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str | None = None


class UsuarioCreate(UsuarioBase):
    password: str  # texto plano en el request; se hashea en el service/crud


class UsuarioUpdate(BaseModel):
    """Todos los campos opcionales: solo se actualiza lo que el request envía."""
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    password: str | None = None  # si se envía, se re-hashea; si no, no se toca


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    rol: RolUsuario
    fecha_registro: datetime
    # OJO: 'password' nunca se expone aquí


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
