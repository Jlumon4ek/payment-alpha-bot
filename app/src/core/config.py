# src/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

class TelegramSettings(BaseSettings):
    TOKEN: str
    CHANNEL_ID: str
    DISCUSSION_GROUP_ID: str

class RedisSettings(BaseSettings):
    REDIS: str

class Settings(DatabaseSettings, TelegramSettings, RedisSettings):
    COMPANY_NAME: str
    
    model_config = SettingsConfigDict(
        env_file = str(Path(__file__).parent.parent.parent / '.env')
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()