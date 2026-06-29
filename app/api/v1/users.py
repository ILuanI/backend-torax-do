from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permisos import ADMIN_ROLE, DOCTOR_ROLE, normalize_role
from app.core.security import get_password_hash
from app.dependencies import require_roles
from app.models.medico import Medico
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[Usuario]:
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).order_by(Usuario.id)
    )
    return list(result.scalars().all())


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> Usuario:
    user = Usuario(**payload.model_dump(exclude={"password"}), password_hash=get_password_hash(payload.password))
    db.add(user)
    await db.flush()

    role = await db.get(Rol, payload.rol_id)
    if role and normalize_role(role.nombre) == DOCTOR_ROLE:
        existing = await db.execute(select(Medico).where(Medico.usuario_id == user.id))
        if existing.scalar_one_or_none() is None:
            db.add(Medico(
                usuario_id=user.id,
                cmp=payload.medico_cmp,
                especialidad=payload.medico_especialidad
            ))

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> Usuario:
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> Usuario:
    user = await db.get(Usuario, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        user.password_hash = get_password_hash(password)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    user = await db.get(Usuario, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
