import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_id: str = os.getenv("app_id", "643703ab")
    app_key: str = os.getenv("app_key", "4e8e9ed71a593771d1bf5c4cd0e70274")
    db_url: str = os.getenv("DB_URL", "sqlite:///train_schedule.db")
    env: str = os.getenv("APP_ENV", "DEV")


settings = Settings()


class Secrets(BaseSettings):
    app_id: str = os.getenv("app_id", "643703ab")
    app_key: str = os.getenv("app_key", "4e8e9ed71a593771d1bf5c4cd0e70274")


secrets = Secrets()
