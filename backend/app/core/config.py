from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = ""
    matcher: Literal["llm", "keyword"] = "keyword"

    database_url: str = ""
    migration_database_url: str = ""
    supabase_url: str = ""

    allowed_origins: str = "http://localhost:5173"

    daily_analysis_limit: int = 20
    max_upload_bytes: int = 4_000_000
    max_cv_chars: int = 20_000
    max_job_chars: int = 10_000

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
