from pydantic import BaseModel, ConfigDict

from app.schemas.permiso import PermisoRead


class RolBase(BaseModel):
    nombre: str
    descripcion: str | None = None


class RolCreate(RolBase):
    permiso_ids: list[int] = []


class RolUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class RolRead(RolBase):
    id: int
    permisos: list[PermisoRead] = []

    model_config = ConfigDict(from_attributes=True)
