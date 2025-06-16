import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_id: str = "643703ab"
    app_key: str = "4e8e9ed71a593771d1bf5c4cd0e70274"
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
logging.info(f"Settings loaded: env={settings.env}, db_url={settings.db_url}")
logging.info("Starting Raj - UK train timetable")

# Automatically create all tables on startup
try:
    from app.uk_train_schedule.models import create_all_tables

    create_all_tables(settings.db_url)
    logging.info("Database tables checked/created on startup.")
except Exception as e:
    logging.error(f"Failed to create tables on startup: {e}")
