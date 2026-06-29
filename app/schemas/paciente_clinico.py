from pydantic import BaseModel

from app.schemas.dato_clinico import DatoClinicoRead
from app.schemas.paciente import PacienteRead
from app.schemas.prediccion import PrediccionRead


class PacienteClinicoRead(BaseModel):
    paciente: PacienteRead
    ultimo_dato_clinico: DatoClinicoRead | None = None
    ultima_prediccion: PrediccionRead | None = None
