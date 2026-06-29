from datetime import date, time

from pydantic import BaseModel, ConfigDict


class DisponibilidadBase(BaseModel):
    medico_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    disponible: bool = True


class DisponibilidadCreate(DisponibilidadBase):
    pass


class DisponibilidadUpdate(BaseModel):
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    disponible: bool | None = None


class DisponibilidadRead(DisponibilidadBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
