from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PrediccionRequest(BaseModel):
    paciente_id: int
    medico_id: int | None = None
    datos_clinicos_id: int | None = None
    cita_id: int | None = None
    modelo: str = "lr"


class PrediccionRead(BaseModel):
    id: int
    paciente_id: int
    medico_id: int | None = None
    datos_clinicos_id: int | None = None
    cita_id: int | None = None
    modelo_utilizado: str
    probabilidad: float
    clase_predicha: str
    nivel_riesgo: str
    imagen_original_path: str | None = None
    imagen_procesada_path: str | None = None
    fecha_prediccion: datetime

    model_config = ConfigDict(from_attributes=True)
