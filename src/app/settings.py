import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_id: str = "add_your_app_id_here"
    app_key: str = "add_your_app_key_here"
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
logger.info(f"Settings loaded: env={settings.env}, db_url={settings.db_url}")
