"""Application configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str = "sqlite:///./fitness_studio.db"
    
    class Config:
        env_file = ".env"


settings = Settings()
