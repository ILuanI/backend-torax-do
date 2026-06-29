from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.prediccion import PrediccionRead


def _naive_local_datetime(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


class CitaBase(BaseModel):
    paciente_id: int
    medico_id: int | None = None
    disponibilidad_id: int | None = None
    fecha_cita: datetime
    motivo_consulta: str | None = None
    observaciones: str | None = None

    @field_validator("fecha_cita", mode="before")
    @classmethod
    def strip_timezone(cls, value: datetime | str) -> datetime | str:
        if isinstance(value, datetime):
            return _naive_local_datetime(value)
        if isinstance(value, str) and value.endswith("Z"):
            return value[:-1] + "+00:00"
        return value

    @field_validator("fecha_cita", mode="after")
    @classmethod
    def ensure_naive(cls, value: datetime) -> datetime:
        return _naive_local_datetime(value)


class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    medico_id: int | None = None
    disponibilidad_id: int | None = None
    fecha_cita: datetime | None = None
    estado: str | None = None
    motivo_consulta: str | None = None
    observaciones: str | None = None

    @field_validator("fecha_cita", mode="before")
    @classmethod
    def strip_timezone(cls, value: datetime | str | None) -> datetime | str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return _naive_local_datetime(value)
        if isinstance(value, str) and value.endswith("Z"):
            return value[:-1] + "+00:00"
        return value

    @field_validator("fecha_cita", mode="after")
    @classmethod
    def ensure_naive(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _naive_local_datetime(value)


class CitaRead(CitaBase):
    id: int
    estado: str
    created_at: datetime
    predicciones: list[PrediccionRead] = []

    model_config = ConfigDict(from_attributes=True)
