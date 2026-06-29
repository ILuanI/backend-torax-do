from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.medico_scope import resolve_medico_id_param
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE, SECRETARY_ROLE
from app.dependencies import get_current_user, require_roles
from app.models.cita import Cita
from app.models.dato_clinico import DatoClinico
from app.models.paciente import Paciente
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.paciente import PacienteCreate, PacienteHistorialRead, PacienteRead, PacienteUpdate

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("", response_model=list[PacienteRead], dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def list_patients(
    search: str | None = None,
    dni: str | None = None,
    medico_id: int | None = None,
    con_datos_clinicos: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[Paciente]:
    effective_medico_id = await resolve_medico_id_param(db, current_user, medico_id)

    query = select(Paciente).distinct()
    if effective_medico_id is not None:
        query = query.join(Cita, Cita.paciente_id == Paciente.id).where(
            Cita.medico_id == effective_medico_id
        )
    if con_datos_clinicos:
        query = query.where(
            exists().where(
                DatoClinico.paciente_id == Paciente.id,
            )
        )
    if dni:
        query = query.where(Paciente.dni == dni)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Paciente.dni.ilike(pattern),
                Paciente.nombres.ilike(pattern),
                Paciente.apellidos.ilike(pattern),
            )
        )
    result = await db.execute(query.order_by(Paciente.id))
    return list(result.scalars().all())


@router.post("", response_model=PacienteRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE))])
async def create_patient(payload: PacienteCreate, db: AsyncSession = Depends(get_db)) -> Paciente:
    patient = Paciente(**payload.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}/historial", response_model=PacienteHistorialRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def get_patient_history(patient_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(Paciente)
        .options(
            selectinload(Paciente.citas),
            selectinload(Paciente.datos_clinicos),
            selectinload(Paciente.predicciones),
            selectinload(Paciente.recomendaciones),
        )
        .where(Paciente.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    citas = sorted(patient.citas, key=lambda c: c.fecha_cita, reverse=True)
    datos_clinicos = sorted(patient.datos_clinicos, key=lambda d: d.fecha_registro, reverse=True)
    predicciones = sorted(patient.predicciones, key=lambda p: p.fecha_prediccion, reverse=True)
    recomendaciones = sorted(patient.recomendaciones, key=lambda r: r.fecha_generacion, reverse=True)

    return {
        "paciente": patient,
        "citas": citas,
        "datos_clinicos": datos_clinicos,
        "predicciones": predicciones,
        "recomendaciones": recomendaciones,
    }


@router.get("/{patient_id}", response_model=PacienteRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)) -> Paciente:
    patient = await db.get(Paciente, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PacienteRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE))])
async def update_patient(patient_id: int, payload: PacienteUpdate, db: AsyncSession = Depends(get_db)) -> Paciente:
    patient = await db.get(Paciente, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE))])
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    result = await db.execute(select(Prediccion).where(Prediccion.paciente_id == patient_id))
    for prediction in result.scalars().all():
        for path in (prediction.imagen_original_path, prediction.imagen_procesada_path):
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except OSError:
                    pass

    patient = await db.get(Paciente, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    await db.delete(patient)
    await db.commit()
    return {"message": "Patient deleted"}
