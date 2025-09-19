from pydantic import BaseSettings, Field
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@db:5432/postgres",
        env="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    storage_root: Path = Field(default=Path("/app/data"), env="STORAGE_ROOT")
    ffmpeg_path: str = Field(default="ffmpeg", env="FFMPEG_PATH")
    ffprobe_path: str = Field(default="ffprobe", env="FFPROBE_PATH")
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")

    class Config:
        env_file = ".env"


settings = Settings()




