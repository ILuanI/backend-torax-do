from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prediccion(Base):
    __tablename__ = "predicciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"), nullable=False, index=True)
    medico_id: Mapped[int | None] = mapped_column(ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    datos_clinicos_id: Mapped[int | None] = mapped_column(ForeignKey("datos_clinicos.id", ondelete="SET NULL"), nullable=True, index=True)
    cita_id: Mapped[int | None] = mapped_column(ForeignKey("citas.id", ondelete="SET NULL"), nullable=True, index=True)
    modelo_utilizado: Mapped[str] = mapped_column(String(20), nullable=False)
    probabilidad: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    clase_predicha: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel_riesgo: Mapped[str] = mapped_column(String(20), nullable=False)
    imagen_original_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagen_procesada_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_prediccion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    paciente = relationship("Paciente", back_populates="predicciones", lazy="selectin")
    medico = relationship("Medico", back_populates="predicciones", lazy="selectin")
    dato_clinico = relationship("DatoClinico", back_populates="predicciones", lazy="selectin")
    cita = relationship("Cita", back_populates="predicciones", lazy="selectin")
    recomendacion = relationship("Recomendacion", back_populates="prediccion", uselist=False)
