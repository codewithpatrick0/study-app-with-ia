from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]  # Project root, where .env lives

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env")
    anthropic_api_key: str
    database_url: str
    jwt_secret_key: str = Field(min_length=32) 
    access_token_expire_minutes: int = 30

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, url: str) -> str:
        """Neon gives 'postgresql://...'; SQLAlchemy needs the driver: 'postgresql+psycopg://...'."""
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

settings = Settings()
