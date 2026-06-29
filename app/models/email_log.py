from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recomendacion_id: Mapped[int | None] = mapped_column(ForeignKey("recomendaciones.id", ondelete="CASCADE"), nullable=True, index=True)
    destinatario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_evento: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    recomendacion = relationship("Recomendacion", back_populates="email_logs", lazy="selectin")
