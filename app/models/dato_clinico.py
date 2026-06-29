from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DatoClinico(Base):
    __tablename__ = "datos_clinicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"), nullable=False, index=True)
    medico_id: Mapped[int | None] = mapped_column(ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    cita_id: Mapped[int | None] = mapped_column(ForeignKey("citas.id", ondelete="SET NULL"), nullable=True, index=True)
    edad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fumador: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    paquetes_anio: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    exposicion_humo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    exposicion_asbesto: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    exposicion_radon: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    antecedente_familiar_cancer: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tos_cronica: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hemoptisis: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    disnea: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    dolor_toracico: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    perdida_peso: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fatiga: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ronquera: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    infecciones_recurrentes: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    paciente = relationship("Paciente", back_populates="datos_clinicos", lazy="selectin")
    medico = relationship("Medico", back_populates="datos_clinicos", lazy="selectin")
    cita = relationship("Cita", lazy="selectin")
    predicciones = relationship("Prediccion", back_populates="dato_clinico")
