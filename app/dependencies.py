from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permisos import normalize_role
from app.core.security import decode_access_token
from app.models.rol import Rol
from app.models.usuario import Usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_error

    result = await db.execute(
        select(Usuario)
        .options(
            selectinload(Usuario.rol).selectinload(Rol.permisos),
            selectinload(Usuario.medico),
        )
        .where(Usuario.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None or not user.activo:
        raise credentials_error
    return user


def require_roles(*roles: str) -> Callable:
    allowed = {normalize_role(role) for role in roles}

    async def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        user_role = normalize_role(current_user.rol.nombre if current_user.rol else None)
        if user_role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return dependency


def require_permissions(*permissions: str) -> Callable:
    async def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        user_permissions = {
            permiso.codigo for permiso in (current_user.rol.permisos if current_user.rol else [])
        }
        if not set(permissions).issubset(user_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency
