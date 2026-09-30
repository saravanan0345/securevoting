import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)


def get_database_url():
    configured_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("STORAGE_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
    )
    fallback_url = f"sqlite:///{(DATABASE_DIR / 'secure_voting.db').resolve()}"

    if not configured_url:
        if os.getenv("VERCEL"):
            raise RuntimeError("Set DATABASE_URL to a persistent PostgreSQL database on Vercel.")
        return fallback_url

    if configured_url.startswith("sqlite:///") and not configured_url.startswith("sqlite:////"):
        relative_path = configured_url.replace("sqlite:///", "", 1)
        if relative_path:
            candidate_path = (BASE_DIR / relative_path).resolve()
            return f"sqlite:///{candidate_path}"

    if configured_url.startswith("postgres://"):
        return configured_url.replace("postgres://", "postgresql+psycopg://", 1)
    if configured_url.startswith("postgresql://"):
        return configured_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return configured_url


if os.getenv("VERCEL") and not all(
    os.getenv(name) for name in ("SECRET_KEY", "VOTING_MASTER_KEY", "ADMIN_PASSWORD")
):
    raise RuntimeError("Set SECRET_KEY, VOTING_MASTER_KEY, and ADMIN_PASSWORD in Vercel settings.")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true" if os.getenv("VERCEL") else "false").lower() in {"1", "true", "yes"}
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@securevoting.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SecureAdmin@123")
    VOTING_MASTER_KEY = os.getenv("VOTING_MASTER_KEY", "secure-voting-demo-master-key")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
