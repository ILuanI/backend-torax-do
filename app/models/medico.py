from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    cmp: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    especialidad: Mapped[str | None] = mapped_column(String(100), default="Neumologia", nullable=True)

    usuario = relationship("Usuario", back_populates="medico", lazy="selectin")
    disponibilidad = relationship("DisponibilidadMedica", back_populates="medico")
    citas = relationship("Cita", back_populates="medico")
    datos_clinicos = relationship("DatoClinico", back_populates="medico")
    predicciones = relationship("Prediccion", back_populates="medico")
