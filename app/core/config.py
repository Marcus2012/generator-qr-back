import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Generador QR Backend"
    
    # DB CONFIG
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "secret")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "qr_backend")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT CONFIG
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key_default")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # GCP CONFIG
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_BUCKET_NAME: str = os.getenv("GCP_BUCKET_NAME", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
