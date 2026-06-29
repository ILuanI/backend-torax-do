from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RecomendacionCreate(BaseModel):
    prediccion_id: int


class RecomendacionRead(BaseModel):
    id: int
    prediccion_id: int
    paciente_id: int | None = None
    medico_id: int | None = None
    contenido_recomendacion: str
    reporte_pdf_path: str | None = None
    email_enviado_a: str | None = None
    email_enviado: bool
    fecha_envio: datetime | None = None
    fecha_generacion: datetime

    model_config = ConfigDict(from_attributes=True)


class SendRecommendationEmailRequest(BaseModel):
    email: EmailStr | None = None
    subject: str = "Reporte medico de prediccion"
