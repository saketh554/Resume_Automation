from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    model_parsing: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./data/resumefit.db"
    data_dir: str = "./data"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def ensure_data_dir(settings: Settings) -> None:
    """Create the configured data directory if missing."""
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
