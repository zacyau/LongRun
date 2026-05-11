from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Long Run"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite:///./long_run_data.db"
    cache_ttl_hours: int = 24

    data_update_hour: int = 20
    data_update_minute: int = 0

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()