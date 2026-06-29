from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.medico_scope import require_medico_id
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE, SECRETARY_ROLE, normalize_role
from app.dependencies import get_current_user, require_roles
from app.models.cita import Cita
from app.models.dato_clinico import DatoClinico
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.medico import MedicoCreate, MedicoRead, MedicoUpdate
from app.schemas.paciente_clinico import PacienteClinicoRead

router = APIRouter(prefix="/medicos", tags=["medicos"])


async def _build_clinical_patient_items(
    db: AsyncSession,
    patient_ids: list[int],
) -> list[PacienteClinicoRead]:
    items: list[PacienteClinicoRead] = []
    for pid in patient_ids:
        patient = await db.get(Paciente, pid)
        if patient is None:
            continue

        dc_result = await db.execute(
            select(DatoClinico)
            .where(DatoClinico.paciente_id == pid)
            .order_by(DatoClinico.fecha_registro.desc())
            .limit(1)
        )
        ultimo_dc = dc_result.scalar_one_or_none()
        if ultimo_dc is None:
            continue

        pred_result = await db.execute(
            select(Prediccion)
            .where(Prediccion.paciente_id == pid)
            .order_by(Prediccion.fecha_prediccion.desc())
            .limit(1)
        )
        ultima_pred = pred_result.scalar_one_or_none()

        items.append(
            PacienteClinicoRead(
                paciente=patient,
                ultimo_dato_clinico=ultimo_dc,
                ultima_prediccion=ultima_pred,
            )
        )
    return items


@router.get("", response_model=list[MedicoRead], dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def list_medicos(db: AsyncSession = Depends(get_db)) -> list[Medico]:
    result = await db.execute(
        select(Medico).options(selectinload(Medico.usuario)).order_by(Medico.id)
    )
    return list(result.scalars().all())


@router.post("", response_model=MedicoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def create_medico(payload: MedicoCreate, db: AsyncSession = Depends(get_db)) -> Medico:
    user = await db.get(Usuario, payload.usuario_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await db.execute(select(Medico).where(Medico.usuario_id == payload.usuario_id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Doctor profile already exists for this user")

    medico = Medico(**payload.model_dump())
    db.add(medico)
    await db.commit()
    result = await db.execute(
        select(Medico).options(selectinload(Medico.usuario)).where(Medico.id == medico.id)
    )
    return result.scalar_one()


@router.get("/me/pacientes-clinicos", response_model=list[PacienteClinicoRead], dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def list_my_clinical_patients(
    medico_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[PacienteClinicoRead]:
    user_role = normalize_role(current_user.rol.nombre if current_user.rol else None)

    if user_role == ADMIN_ROLE:
        if medico_id is not None:
            result = await db.execute(
                select(Paciente.id)
                .join(Cita, Cita.paciente_id == Paciente.id)
                .where(Cita.medico_id == medico_id)
                .distinct()
            )
            patient_ids = [row[0] for row in result.all()]
        else:
            result = await db.execute(
                select(DatoClinico.paciente_id).distinct()
            )
            patient_ids = [row[0] for row in result.all()]
        return await _build_clinical_patient_items(db, patient_ids)

    effective_medico_id = await require_medico_id(db, current_user)

    result = await db.execute(
        select(Paciente.id)
        .join(Cita, Cita.paciente_id == Paciente.id)
        .where(Cita.medico_id == effective_medico_id)
        .distinct()
    )
    patient_ids = [row[0] for row in result.all()]
    return await _build_clinical_patient_items(db, patient_ids)


@router.get("/{medico_id}", response_model=MedicoRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def get_medico(medico_id: int, db: AsyncSession = Depends(get_db)) -> Medico:
    result = await db.execute(
        select(Medico).options(selectinload(Medico.usuario)).where(Medico.id == medico_id)
    )
    medico = result.scalar_one_or_none()
    if medico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return medico


@router.patch("/{medico_id}", response_model=MedicoRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def update_medico(medico_id: int, payload: MedicoUpdate, db: AsyncSession = Depends(get_db)) -> Medico:
    result = await db.execute(
        select(Medico).options(selectinload(Medico.usuario)).where(Medico.id == medico_id)
    )
    medico = result.scalar_one_or_none()
    if medico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(medico, key, value)

    await db.commit()
    await db.refresh(medico)
    return medico
