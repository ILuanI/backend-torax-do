from pydantic import BaseModel, ConfigDict


class MedicoUsuarioRead(BaseModel):
    id: int
    nombre_completo: str
    email: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class MedicoBase(BaseModel):
    usuario_id: int
    cmp: str | None = None
    especialidad: str | None = "Neumologia"


class MedicoCreate(BaseModel):
    usuario_id: int
    cmp: str | None = None
    especialidad: str | None = "Neumologia"


class MedicoUpdate(BaseModel):
    cmp: str | None = None
    especialidad: str | None = None


class MedicoRead(MedicoBase):
    id: int
    usuario: MedicoUsuarioRead | None = None

    model_config = ConfigDict(from_attributes=True)
