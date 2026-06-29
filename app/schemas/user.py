from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.rol import RolRead


class UserBase(BaseModel):
    rol_id: int
    nombre_completo: str
    email: EmailStr
    username: str
    activo: bool = True


class UserCreate(UserBase):
    password: str
    medico_cmp: str | None = None
    medico_especialidad: str | None = "Neumologia"


class UserUpdate(BaseModel):
    rol_id: int | None = None
    nombre_completo: str | None = None
    email: EmailStr | None = None
    username: str | None = None
    activo: bool | None = None
    password: str | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    rol: RolRead | None = None
    medico_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
