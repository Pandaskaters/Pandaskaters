from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "PandaSkaters"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite+aiosqlite:///./pandaskaters.db"

    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    BASE_FARE_ECONOMY: float = 3.00
    BASE_FARE_PREMIUM: float = 5.00
    BASE_FARE_MOTO: float = 2.00
    PER_KM_ECONOMY: float = 0.80
    PER_KM_PREMIUM: float = 1.50
    PER_KM_MOTO: float = 0.50

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5242880

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
