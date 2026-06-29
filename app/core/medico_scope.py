from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permisos import DOCTOR_ROLE, normalize_role
from app.models.medico import Medico
from app.models.usuario import Usuario


async def get_medico_id_for_user(db: AsyncSession, user: Usuario) -> int | None:
    if user.medico is not None:
        return user.medico.id
    result = await db.execute(select(Medico.id).where(Medico.usuario_id == user.id))
    return result.scalar_one_or_none()


async def require_medico_id(db: AsyncSession, user: Usuario) -> int:
    medico_id = await get_medico_id_for_user(db, user)
    if medico_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor profile not found for this user",
        )
    return medico_id


def is_doctor(user: Usuario) -> bool:
    role = normalize_role(user.rol.nombre if user.rol else None)
    return role == DOCTOR_ROLE


async def resolve_medico_id_param(
    db: AsyncSession,
    user: Usuario,
    medico_id: int | None,
) -> int | None:
    if is_doctor(user):
        return await require_medico_id(db, user)
    return medico_id


async def load_user_with_medico(db: AsyncSession, user_id: int) -> Usuario | None:
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.medico)).where(Usuario.id == user_id)
    )
    return result.scalar_one_or_none()
