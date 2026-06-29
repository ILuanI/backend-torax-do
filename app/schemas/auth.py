from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class RegisterUserRequest(BaseModel):
    rol_id: int
    nombre_completo: str
    email: EmailStr
    username: str
    password: str
