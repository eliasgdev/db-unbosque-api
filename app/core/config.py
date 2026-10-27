from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    cors_origins: list[str] = ["http://localhost:4200"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
