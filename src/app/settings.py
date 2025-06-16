import logging

from pydantic_settings import BaseSettings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_id: str = "uk_train_schedule"
    app_key: str = "your_api_key_here"  # Replace with your actual API key
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
logger.info(f"Settings loaded: env={settings.env}, db_url={settings.db_url}")
logger.info("Starting Raj - UK train timetable")

# Automatically create all tables on startup
try:
    from app.uk_train_schedule.models import create_all_tables

    create_all_tables(settings.db_url)
    logger.info("Database tables checked/created on startup.")
except Exception as e:
    logger.error(f"Failed to create tables on startup: {e}")
