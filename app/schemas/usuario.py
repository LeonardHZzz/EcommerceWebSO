from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.usuario import RolUsuario


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str | None = None


class UsuarioCreate(UsuarioBase):
    password: str 


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    rol: RolUsuario
    fecha_registro: datetime


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
