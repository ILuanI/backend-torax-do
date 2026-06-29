from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permisos import ADMIN_ROLE
from app.dependencies import require_roles
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.schemas.permiso import PermisoCreate, PermisoRead
from app.schemas.rol import RolCreate, RolRead, RolUpdate

router = APIRouter(prefix="/roles-permisos", tags=["roles-permisos"])


@router.get("/roles", response_model=list[RolRead], dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def list_roles(db: AsyncSession = Depends(get_db)) -> list[Rol]:
    result = await db.execute(select(Rol).options(selectinload(Rol.permisos)).order_by(Rol.id))
    return list(result.scalars().all())


@router.post("/roles", response_model=RolRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def create_role(payload: RolCreate, db: AsyncSession = Depends(get_db)) -> Rol:
    role = Rol(nombre=payload.nombre, descripcion=payload.descripcion)
    if payload.permiso_ids:
        result = await db.execute(select(Permiso).where(Permiso.id.in_(payload.permiso_ids)))
        role.permisos = list(result.scalars().all())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.patch("/roles/{role_id}", response_model=RolRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def update_role(role_id: int, payload: RolUpdate, db: AsyncSession = Depends(get_db)) -> Rol:
    result = await db.execute(
        select(Rol).options(selectinload(Rol.permisos)).where(Rol.id == role_id)
    )
    role = result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(role, key, value)

    await db.commit()
    await db.refresh(role)
    return role


@router.get("/permisos", response_model=list[PermisoRead], dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def list_permissions(db: AsyncSession = Depends(get_db)) -> list[Permiso]:
    result = await db.execute(select(Permiso).order_by(Permiso.id))
    return list(result.scalars().all())


@router.post("/permisos", response_model=PermisoRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def create_permission(payload: PermisoCreate, db: AsyncSession = Depends(get_db)) -> Permiso:
    permission = Permiso(**payload.model_dump())
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission


@router.post("/roles/{role_id}/permisos/{permission_id}", response_model=RolRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def assign_permission(role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)) -> Rol:
    result = await db.execute(
        select(Rol).options(selectinload(Rol.permisos)).where(Rol.id == role_id)
    )
    role = result.scalar_one_or_none()
    permission = await db.get(Permiso, permission_id)
    if role is None or permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role or permission not found")
    if permission not in role.permisos:
        role.permisos.append(permission)
        await db.commit()
        await db.refresh(role)
    return role


@router.delete("/roles/{role_id}/permisos/{permission_id}", response_model=RolRead, dependencies=[Depends(require_roles(ADMIN_ROLE))])
async def remove_permission(role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)) -> Rol:
    result = await db.execute(
        select(Rol).options(selectinload(Rol.permisos)).where(Rol.id == role_id)
    )
    role = result.scalar_one_or_none()
    permission = await db.get(Permiso, permission_id)
    if role is None or permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role or permission not found")
    if permission in role.permisos:
        role.permisos.remove(permission)
        await db.commit()
        await db.refresh(role)
    return role
