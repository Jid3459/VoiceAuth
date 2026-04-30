from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    debug: bool = False  # Add this line
    cors_origins: str  # or List[str] if you handle parsing
    log_level: str = "INFO" 
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SIMILARITY_THRESHOLD_STRONG: float = 0.75
    SIMILARITY_THRESHOLD_WEAK: float = 0.50
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Optional: This prevents the error if other extra vars exist
@lru_cache()
def get_settings():
    return Settings()