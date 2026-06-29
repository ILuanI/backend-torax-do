from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE, SECRETARY_ROLE
from app.dependencies import require_roles
from app.models.cita import Cita
from app.schemas.cita import CitaCreate, CitaRead, CitaUpdate

router = APIRouter(prefix="/citas", tags=["citas"])


@router.get("", response_model=list[CitaRead], dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def list_appointments(
    paciente_id: int | None = None,
    medico_id: int | None = None,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Cita]:
    query = select(Cita).options(selectinload(Cita.predicciones))
    if paciente_id is not None:
        query = query.where(Cita.paciente_id == paciente_id)
    if medico_id is not None:
        query = query.where(Cita.medico_id == medico_id)
    if estado is not None:
        query = query.where(Cita.estado == estado)
    if fecha_desde is not None:
        query = query.where(Cita.fecha_cita >= fecha_desde)
    if fecha_hasta is not None:
        query = query.where(Cita.fecha_cita <= fecha_hasta)
    result = await db.execute(query.order_by(Cita.fecha_cita.desc()))
    return list(result.scalars().all())


@router.post("", response_model=CitaRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE))])
async def create_appointment(payload: CitaCreate, db: AsyncSession = Depends(get_db)) -> Cita:
    appointment = Cita(**payload.model_dump())
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=CitaRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)) -> Cita:
    appointment = await db.get(Cita, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=CitaRead, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def update_appointment(appointment_id: int, payload: CitaUpdate, db: AsyncSession = Depends(get_db)) -> Cita:
    appointment = await db.get(Cita, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE))])
async def delete_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    appointment = await db.get(Cita, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    await db.delete(appointment)
    await db.commit()
    return {"message": "Appointment deleted"}
