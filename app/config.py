from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    TOKEN: str
    CHANNEL_ID: str
    REDIS: str
    COMPANY_NAME: str
    
    class Config:
        env_file = str(Path(__file__).parent / '.env')
    

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
