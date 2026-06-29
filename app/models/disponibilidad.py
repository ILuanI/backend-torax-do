from datetime import date, time

from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DisponibilidadMedica(Base):
    __tablename__ = "disponibilidad_medica"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    medico_id: Mapped[int] = mapped_column(ForeignKey("medicos.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    medico = relationship("Medico", back_populates="disponibilidad", lazy="selectin")
