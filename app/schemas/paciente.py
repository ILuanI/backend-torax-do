from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


from app.schemas.cita import CitaRead
from app.schemas.dato_clinico import DatoClinicoRead
from app.schemas.prediccion import PrediccionRead
from app.schemas.recomendacion import RecomendacionRead


class PacienteBase(BaseModel):
    dni: str | None = None
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    direccion: str | None = None


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    dni: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    direccion: str | None = None


class PacienteRead(PacienteBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PacienteHistorialRead(BaseModel):
    paciente: PacienteRead
    citas: list[CitaRead]
    datos_clinicos: list[DatoClinicoRead]
    predicciones: list[PrediccionRead]
    recomendaciones: list[RecomendacionRead]
