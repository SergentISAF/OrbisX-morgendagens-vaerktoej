from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://orbisx:orbisx_dev@localhost:5432/orbisx"
    redis_url: str = "redis://localhost:6379/0"

    orbisx_api_base: str = "https://yifub04z0f.execute-api.eu-north-1.amazonaws.com/v2"
    orbisx_api_key: str | None = None

    cors_origins: list[str] = ["http://localhost:4321", "http://localhost:3000"]


settings = Settings()
