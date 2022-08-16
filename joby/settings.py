# coding: utf-8
from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings, SecretStr, Field


class Settings(BaseSettings):
    jobs_file_path: Path = Field(..., env="JOBS_FILE_PATH")

    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    postgres_database: str = Field(..., env="POSTGRES_DATABASE")

    max_retry_on_failure: int | None = Field(3, env="MAX_RETRY_ON_FAILURE")

    class Config:
        env_file = Path().resolve() / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
