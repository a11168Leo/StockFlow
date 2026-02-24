import os
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
if load_dotenv:
    load_dotenv(dotenv_path=ENV_PATH, override=False)


class Settings:
    jwt_secret: str
    jwt_algorithm: str
    access_token_minutes: int
    refresh_token_days: int
    cors_allow_origins: list[str]
    app_env: str
    rate_limit_default: str

    def __init__(self) -> None:
        self.jwt_secret = os.getenv("JWT_SECRET", "change-me-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_minutes = int(os.getenv("JWT_ACCESS_MINUTES", "30"))
        self.refresh_token_days = int(os.getenv("JWT_REFRESH_DAYS", "7"))
        self.cors_allow_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ]
        self.app_env = os.getenv("APP_ENV", "development")
        self.rate_limit_default = os.getenv("RATE_LIMIT_DEFAULT", "120/minute")


@lru_cache
def get_settings() -> Settings:
    return Settings()
