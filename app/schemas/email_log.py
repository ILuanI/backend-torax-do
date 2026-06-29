from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmailLogRead(BaseModel):
    id: int
    recomendacion_id: int | None = None
    destinatario: str | None = None
    estado: str | None = None
    mensaje: str | None = None
    fecha_evento: datetime

    model_config = ConfigDict(from_attributes=True)
