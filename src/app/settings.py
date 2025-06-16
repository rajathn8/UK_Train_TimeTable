from pydantic_settings import BaseSettings


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
