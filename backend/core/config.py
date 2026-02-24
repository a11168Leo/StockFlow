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
    frontend_reset_url: str
    password_reset_minutes: int
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str
    smtp_use_tls: bool

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
        self.frontend_reset_url = os.getenv("FRONTEND_RESET_URL", "http://localhost:3000/login/")
        self.password_reset_minutes = int(os.getenv("PASSWORD_RESET_MINUTES", "30"))
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "no-reply@stockflow.local")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
