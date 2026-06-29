from pydantic import BaseModel, ConfigDict


class PermisoBase(BaseModel):
    codigo: str
    descripcion: str | None = None


class PermisoCreate(PermisoBase):
    pass


class PermisoRead(PermisoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
