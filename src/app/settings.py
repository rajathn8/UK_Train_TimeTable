import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_id: str
    app_key: str
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
