from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_name: str = 'ShadowByte Gateway'
    app_version: str = '0.1.0'
    app_port: int = 8000
    database_url: str = ''
    redis_url: str = ''
    redis_token: str = ''
    qdrant_url: str = 'http://localhost:6333'
    qdrant_api_key: str = ''
    frontend_origins: str = 'http://localhost:5173'

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(',') if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
