from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.file_storage import file_storage
from app.core.medico_scope import is_doctor, require_medico_id
from app.core.modelos_ia.load import predict
from app.core.modelos_ia.preprocess import preprocess_radiografia
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE
from app.dependencies import get_current_user, require_roles
from app.models.dato_clinico import DatoClinico
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.prediccion import PrediccionRead

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


async def _validate_prediction_references(
    db: AsyncSession,
    paciente_id: int,
    medico_id: int,
    datos_clinicos_id: int | None,
) -> None:
    patient = await db.get(Paciente, paciente_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    medico = await db.get(Medico, medico_id)
    if medico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if datos_clinicos_id is not None:
        clinical_data = await db.get(DatoClinico, datos_clinicos_id)
        if clinical_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinical data not found")
        if clinical_data.paciente_id != paciente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Clinical data does not belong to the specified patient",
            )


@router.get("", response_model=list[PrediccionRead], dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def list_predictions(
    paciente_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Prediccion]:
    query = select(Prediccion)
    if paciente_id is not None:
        query = query.where(Prediccion.paciente_id == paciente_id)
    result = await db.execute(query.order_by(Prediccion.id.desc()))
    return list(result.scalars().all())


@router.post("", response_model=PrediccionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def create_prediction(
    paciente_id: int = Form(...),
    medico_id: int | None = Form(None),
    modelo: str = Form("lr"),
    datos_clinicos_id: int | None = Form(None),
    cita_id: int | None = Form(None),
    radiografia: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Prediccion:
    effective_medico_id = medico_id
    if is_doctor(current_user):
        effective_medico_id = await require_medico_id(db, current_user)
    elif effective_medico_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="medico_id is required")

    await _validate_prediction_references(db, paciente_id, effective_medico_id, datos_clinicos_id)

    try:
        original_path = await file_storage.save_upload(radiografia)
        processed_path = file_storage.processed_image_path()
        features = preprocess_radiografia(original_path, processed_path)
        result, probability = predict(modelo, features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    prediction = Prediccion(
        paciente_id=paciente_id,
        medico_id=effective_medico_id,
        datos_clinicos_id=datos_clinicos_id,
        cita_id=cita_id,
        modelo_utilizado=modelo.lower(),
        clase_predicha=result,
        probabilidad=probability or 0.0,
        nivel_riesgo="alto" if result == "positivo" and (probability or 0) >= 0.7 else "medio" if result == "positivo" else "bajo",
        imagen_original_path=str(original_path),
        imagen_procesada_path=str(processed_path),
    )
    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)
    return prediction


@router.get("/{prediction_id}", response_model=PrediccionRead, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def get_prediction(prediction_id: int, db: AsyncSession = Depends(get_db)) -> Prediccion:
    prediction = await db.get(Prediccion, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    return prediction
