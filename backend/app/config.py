from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+aiomysql://journeyforge:journeyforge_pass@localhost:3306/journeyforge"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Gemini AI
    gemini_api_key: str = ""

    # Ollama AI (Local model)
    use_ollama: bool = False
    ollama_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "gemma2:2b"

    # App
    app_name: str = "JourneyForge API"
    debug: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
