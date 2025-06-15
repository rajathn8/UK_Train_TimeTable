import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_id: str = os.getenv("app_id", "")
    app_key: str = os.getenv("app_key", "")
    db_url: str = os.getenv("DB_URL", "sqlite:///train_schedule.db")
    env: str = os.getenv("APP_ENV", "DEV")


settings = Settings()
