from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="postgresql+asyncpg://user:password@localhost:5432/database_name")
    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)

    gemini_api_key: str = Field(default="")

    mail_username: str = Field(default="")
    mail_password: str = Field(default="")
    mail_from: str = Field(default="")
    mail_port: int = Field(default=587)
    mail_server: str = Field(default="")
    mail_starttls: bool = Field(default=True)
    mail_ssl_tls: bool = Field(default=False)

    upload_dir: str = Field(default="uploads")
    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)
    app_debug: bool = Field(default=True)
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173",
    )
    model_lr_path: str = Field(default="models_ia/modelo_lr.joblib")
    model_rf_path: str = Field(default="models_ia/modelo_rf.joblib")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @field_validator("access_token_expire_minutes", mode="before")
    @classmethod
    def default_token_minutes(cls, value: Any) -> Any:
        return 60 if value == "" or value is None else value

    @field_validator("database_url", mode="before")
    @classmethod
    def default_database_url(cls, value: Any) -> Any:
        if value == "" or value is None:
            return "postgresql+asyncpg://user:password@localhost:5432/database_name"
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("mail_port", mode="before")
    @classmethod
    def default_mail_port(cls, value: Any) -> Any:
        return 587 if value == "" or value is None else value

    @field_validator("mail_starttls", mode="before")
    @classmethod
    def default_mail_starttls(cls, value: Any) -> Any:
        return True if value == "" or value is None else value

    @field_validator("mail_ssl_tls", mode="before")
    @classmethod
    def default_mail_ssl_tls(cls, value: Any) -> Any:
        return False if value == "" or value is None else value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
