from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.core.database import get_db
from app.core.email_service import send_email_with_attachment
from app.core.gemini_service import gemini_service
from app.core.pdf_generator import generate_recommendation_pdf
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE
from app.dependencies import require_roles
from app.models.email_log import EmailLog
from app.models.prediccion import Prediccion
from app.models.recomendacion import Recomendacion
from app.schemas.email_log import EmailLogRead
from app.schemas.recomendacion import RecomendacionRead

router = APIRouter(prefix="/recomendaciones", tags=["recomendaciones"])


@router.get("", response_model=list[RecomendacionRead], dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def list_recommendations(
    paciente_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Recomendacion]:
    query = select(Recomendacion)
    if paciente_id is not None:
        query = query.where(Recomendacion.paciente_id == paciente_id)
    result = await db.execute(query.order_by(Recomendacion.id.desc()))
    return list(result.scalars().all())


@router.post("/predicciones/{prediction_id}", response_model=RecomendacionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def create_recommendation(prediction_id: int, db: AsyncSession = Depends(get_db)) -> Recomendacion:
    result = await db.execute(
        select(Prediccion)
        .options(
            selectinload(Prediccion.paciente),
            selectinload(Prediccion.dato_clinico),
            selectinload(Prediccion.recomendacion),
        )
        .where(Prediccion.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    if prediction.recomendacion is not None:
        return prediction.recomendacion

    content = await gemini_service.generate_recommendation(prediction, prediction.dato_clinico)
    pdf_path = generate_recommendation_pdf(prediction.paciente, prediction, content)
    recommendation = Recomendacion(
        paciente_id=prediction.paciente_id,
        medico_id=prediction.medico_id,
        prediccion_id=prediction.id,
        contenido_recomendacion=content,
        reporte_pdf_path=str(pdf_path),
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(recommendation)
    return recommendation


@router.post("/{recommendation_id}/send-email", dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def send_recommendation_email(
    recommendation_id: int,
    email: str | None = Form(None),
    subject: str = Form("Reporte medico de prediccion"),
    mensaje: str | None = Form(None),
    archivo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    result = await db.execute(
        select(Recomendacion)
        .options(selectinload(Recomendacion.paciente))
        .where(Recomendacion.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()
    if recommendation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    recipient = email or recommendation.paciente.email
    if not recipient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient email is not available")

    body = mensaje or recommendation.contenido_recomendacion
    attachment_path: str | Path | None = recommendation.reporte_pdf_path
    temp_path: Path | None = None

    if archivo is not None and archivo.filename:
        suffix = Path(archivo.filename).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await archivo.read()
            tmp.write(content)
            temp_path = Path(tmp.name)
            attachment_path = temp_path

    log = EmailLog(
        recomendacion_id=recommendation.id,
        destinatario=recipient,
        estado="pendiente",
    )
    db.add(log)

    try:
        await send_email_with_attachment(
            recipient=recipient,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
        )
        log.estado = "enviado"
        recommendation.email_enviado = True
        recommendation.email_enviado_a = recipient
        recommendation.fecha_envio = datetime.utcnow()
    except Exception as exc:
        log.estado = "error"
        log.mensaje = str(exc)
        await db.commit()
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)

    await db.commit()
    return {"message": "Email sent"}


@router.get("/{recommendation_id}/pdf", dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def download_recommendation_pdf(recommendation_id: int, db: AsyncSession = Depends(get_db)) -> FileResponse:
    recommendation = await db.get(Recomendacion, recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    if not recommendation.reporte_pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report not available")

    pdf_path = Path(recommendation.reporte_pdf_path)
    if not pdf_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found on disk")

    return FileResponse(path=pdf_path, media_type="application/pdf", filename=pdf_path.name)


@router.get("/{recommendation_id}/email-logs", response_model=list[EmailLogRead], dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def list_recommendation_email_logs(recommendation_id: int, db: AsyncSession = Depends(get_db)) -> list[EmailLog]:
    recommendation = await db.get(Recomendacion, recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    result = await db.execute(
        select(EmailLog)
        .where(EmailLog.recomendacion_id == recommendation_id)
        .order_by(EmailLog.fecha_evento.desc())
    )
    return list(result.scalars().all())


@router.get("/{recommendation_id}", response_model=RecomendacionRead, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def get_recommendation(recommendation_id: int, db: AsyncSession = Depends(get_db)) -> Recomendacion:
    recommendation = await db.get(Recomendacion, recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return recommendation
