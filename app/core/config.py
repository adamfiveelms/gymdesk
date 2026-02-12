from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "AdamDesk"
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./adamdesk.db"
    )


settings = Settings()
