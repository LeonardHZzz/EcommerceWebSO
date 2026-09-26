from pydantic import BaseModel, ConfigDict, Field


class RecintoBase(BaseModel):
    nombre_recinto: str
    direccion: str
    distrito: str | None = None
    aforo_maximo: int = Field(gt=0)


class RecintoCreate(RecintoBase):
    pass


class RecintoUpdate(BaseModel):
    nombre_recinto: str | None = None
    direccion: str | None = None
    distrito: str | None = None
    aforo_maximo: int | None = Field(default=None, gt=0)


class RecintoOut(RecintoBase):
    model_config = ConfigDict(from_attributes=True)
    id_recinto: int
