import logging

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine

from app.uk_train_schedule.models import Base

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_id: str = "uk_train_schedule"
    app_key: str = "your_api_key_here"
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()

try:
    engine = create_engine(settings.db_url)
    Base.metadata.create_all(engine)
except Exception as e:
    logger.error(f"Failed to create tables on startup: {e}")
