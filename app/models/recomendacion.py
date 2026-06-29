from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Recomendacion(Base):
    __tablename__ = "recomendaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prediccion_id: Mapped[int] = mapped_column(ForeignKey("predicciones.id", ondelete="CASCADE"), nullable=False)
    paciente_id: Mapped[int | None] = mapped_column(ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=True, index=True)
    medico_id: Mapped[int | None] = mapped_column(ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    contenido_recomendacion: Mapped[str] = mapped_column(Text, nullable=False)
    reporte_pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_enviado_a: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email_enviado: Mapped[bool] = mapped_column(default=False, nullable=False)
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    paciente = relationship("Paciente", back_populates="recomendaciones", lazy="selectin")
    prediccion = relationship("Prediccion", back_populates="recomendacion", lazy="selectin")
    email_logs = relationship("EmailLog", back_populates="recomendacion")
