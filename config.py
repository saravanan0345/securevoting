import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)


def get_database_url():
    configured_url = os.getenv("DATABASE_URL")
    fallback_url = f"sqlite:///{(DATABASE_DIR / 'secure_voting.db').resolve()}"

    if not configured_url:
        return fallback_url

    if configured_url.startswith("sqlite:///") and not configured_url.startswith("sqlite:////"):
        relative_path = configured_url.replace("sqlite:///", "", 1)
        if relative_path:
            candidate_path = (BASE_DIR / relative_path).resolve()
            return f"sqlite:///{candidate_path}"

    return configured_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@securevoting.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SecureAdmin@123")
    VOTING_MASTER_KEY = os.getenv("VOTING_MASTER_KEY", "secure-voting-demo-master-key")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
