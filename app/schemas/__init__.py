from app.schemas.auth import LoginRequest, PasswordChange, RegisterUserRequest, Token
from app.schemas.cita import CitaCreate, CitaRead, CitaUpdate
from app.schemas.dato_clinico import DatoClinicoCreate, DatoClinicoRead, DatoClinicoUpdate
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadRead, DisponibilidadUpdate
from app.schemas.paciente import PacienteCreate, PacienteRead, PacienteUpdate
from app.schemas.permiso import PermisoCreate, PermisoRead
from app.schemas.prediccion import PrediccionRead, PrediccionRequest
from app.schemas.recomendacion import RecomendacionCreate, RecomendacionRead
from app.schemas.rol import RolCreate, RolRead
from app.schemas.user import UserCreate, UserRead, UserUpdate

__all__ = [
    "CitaCreate",
    "CitaRead",
    "CitaUpdate",
    "DatoClinicoCreate",
    "DatoClinicoRead",
    "DatoClinicoUpdate",
    "DisponibilidadCreate",
    "DisponibilidadRead",
    "DisponibilidadUpdate",
    "LoginRequest",
    "PacienteCreate",
    "PacienteRead",
    "PacienteUpdate",
    "PasswordChange",
    "PermisoCreate",
    "PermisoRead",
    "PrediccionRead",
    "PrediccionRequest",
    "RecomendacionCreate",
    "RecomendacionRead",
    "RegisterUserRequest",
    "RolCreate",
    "RolRead",
    "Token",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
