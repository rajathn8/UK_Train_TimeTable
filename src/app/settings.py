from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_id: str = "11231"
    app_key: str = "123121"
    db_url: str = "sqlite:///train_schedule.db"
    env: str = "DEV"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
