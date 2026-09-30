import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Career Maps API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/careermaps")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b3a4a7536d5b0669e71168f6a31952e80554ff46b412e2f694b29bb88ed195c8")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
