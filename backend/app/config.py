from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


UNSAFE_SECRET_KEYS = {
    "dev-secret-key-change-in-production",
    "change-me-to-a-random-secret-key",
    "change-me",
}


class Settings(BaseSettings):
    APP_NAME: str = "项目管理系统"
    DEBUG: bool = Field(default=False, validation_alias="APP_DEBUG")

    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    DATABASE_URL_SYNC: str = "sqlite:///./dev.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_allow_credentials(self) -> bool:
        return "*" not in self.cors_origins

    @model_validator(mode="after")
    def validate_secret_key(self):
        if self.DEBUG and not self.SECRET_KEY:
            self.SECRET_KEY = "dev-secret-key-change-in-production"
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be configured")
        if not self.DEBUG and self.SECRET_KEY in UNSAFE_SECRET_KEYS:
            raise ValueError("SECRET_KEY is using an unsafe development value")
        return self

    class Config:
        env_file = ".env"


settings = Settings()
