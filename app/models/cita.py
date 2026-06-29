from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"), nullable=False, index=True)
    medico_id: Mapped[int | None] = mapped_column(ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    disponibilidad_id: Mapped[int | None] = mapped_column(ForeignKey("disponibilidad_medica.id", ondelete="SET NULL"), nullable=True)
    fecha_cita: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(40), default="pendiente", nullable=False)
    motivo_consulta: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    paciente = relationship("Paciente", back_populates="citas", lazy="selectin")
    medico = relationship("Medico", back_populates="citas", lazy="selectin")
    predicciones = relationship("Prediccion", back_populates="cita", lazy="selectin")
