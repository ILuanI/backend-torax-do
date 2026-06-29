from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatoClinicoBase(BaseModel):
    paciente_id: int
    medico_id: int | None = None
    cita_id: int | None = None
    edad: int | None = None
    fumador: bool | None = None
    paquetes_anio: float | None = None
    exposicion_humo: bool | None = None
    exposicion_asbesto: bool | None = None
    exposicion_radon: bool | None = None
    antecedente_familiar_cancer: bool | None = None
    tos_cronica: bool | None = None
    hemoptisis: bool | None = None
    disnea: bool | None = None
    dolor_toracico: bool | None = None
    perdida_peso: bool | None = None
    fatiga: bool | None = None
    ronquera: bool | None = None
    infecciones_recurrentes: bool | None = None
    observaciones: str | None = None


class DatoClinicoCreate(DatoClinicoBase):
    pass


class DatoClinicoUpdate(BaseModel):
    edad: int | None = None
    fumador: bool | None = None
    paquetes_anio: float | None = None
    exposicion_humo: bool | None = None
    exposicion_asbesto: bool | None = None
    exposicion_radon: bool | None = None
    antecedente_familiar_cancer: bool | None = None
    tos_cronica: bool | None = None
    hemoptisis: bool | None = None
    disnea: bool | None = None
    dolor_toracico: bool | None = None
    perdida_peso: bool | None = None
    fatiga: bool | None = None
    ronquera: bool | None = None
    infecciones_recurrentes: bool | None = None
    observaciones: str | None = None


class DatoClinicoRead(DatoClinicoBase):
    id: int
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)
