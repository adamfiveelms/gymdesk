import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "AdamDesk"
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    # Vercel/serverless filesystems are read-only except /tmp.
    # Use /tmp for local fallback when DATABASE_URL is not provided.
    database_url: str = os.getenv("DATABASE_URL", "sqlite:////tmp/adamdesk.db")


settings = Settings()
