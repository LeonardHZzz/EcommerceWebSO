from pydantic import BaseModel, ConfigDict


class CategoriaBase(BaseModel):
    nombre_categoria: str
    descripcion: str | None = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre_categoria: str | None = None
    descripcion: str | None = None


class CategoriaOut(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)
    id_categoria: int
