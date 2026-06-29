from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.medico_scope import is_doctor, require_medico_id
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE, SECRETARY_ROLE
from app.dependencies import get_current_user, require_roles
from app.models.disponibilidad import DisponibilidadMedica
from app.models.usuario import Usuario
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadRead, DisponibilidadUpdate

router = APIRouter(prefix="/disponibilidad", tags=["disponibilidad"])


async def _ensure_availability_owner(
    db: AsyncSession,
    user: Usuario,
    item: DisponibilidadMedica,
) -> None:
    if not is_doctor(user):
        return
    medico_id = await require_medico_id(db, user)
    if item.medico_id != medico_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your availability slot")


@router.get("", response_model=list[DisponibilidadRead], dependencies=[Depends(require_roles(ADMIN_ROLE, SECRETARY_ROLE, DOCTOR_ROLE))])
async def list_availability(
    medico_id: int | None = None,
    fecha: date | None = None,
    disponible: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[DisponibilidadMedica]:
    query = select(DisponibilidadMedica)
    if is_doctor(current_user):
        medico_id = await require_medico_id(db, current_user)
    if medico_id is not None:
        query = query.where(DisponibilidadMedica.medico_id == medico_id)
    if fecha is not None:
        query = query.where(DisponibilidadMedica.fecha == fecha)
    if disponible is not None:
        query = query.where(DisponibilidadMedica.disponible == disponible)
    result = await db.execute(query.order_by(DisponibilidadMedica.medico_id, DisponibilidadMedica.fecha))
    return list(result.scalars().all())


@router.post("", response_model=DisponibilidadRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def create_availability(
    payload: DisponibilidadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> DisponibilidadMedica:
    data = payload.model_dump()
    if is_doctor(current_user):
        data["medico_id"] = await require_medico_id(db, current_user)
    item = DisponibilidadMedica(**data)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{availability_id}", response_model=DisponibilidadRead, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def update_availability(
    availability_id: int,
    payload: DisponibilidadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> DisponibilidadMedica:
    item = await db.get(DisponibilidadMedica, availability_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    await _ensure_availability_owner(db, current_user, item)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{availability_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(ADMIN_ROLE, DOCTOR_ROLE))])
async def delete_availability(
    availability_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    item = await db.get(DisponibilidadMedica, availability_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    await _ensure_availability_owner(db, current_user, item)
    await db.delete(item)
    await db.commit()
    return {"message": "Availability deleted"}
