# config.py - Configuration Management for SmartFormsGPT

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    APP_NAME: str = "SmartFormsGPT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./smartforms.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/smartforms.log"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "pdf,png,jpg,jpeg"
    UPLOAD_DIR: str = "uploads"
    
    # Business Rules
    MAX_CLAIM_AMOUNT: float = 100000.0
    AUTO_APPROVE_THRESHOLD: float = 1000.0
    MAX_SERVICE_AGE_DAYS: int = 365
    MIN_DOCUMENTATION_SCORE: float = 0.5
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Feature Flags
    ENABLE_AI_PROCESSING: bool = True
    ENABLE_BATCH_PROCESSING: bool = False
    ENABLE_ANALYTICS: bool = True
    
    @validator("OPENAI_API_KEY")
    def validate_openai_key(cls, v, values):
        """Validate OpenAI API key if AI processing is enabled."""
        if values.get("ENABLE_AI_PROCESSING") and not v:
            raise ValueError("OPENAI_API_KEY is required when AI processing is enabled")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Validate secret key in production."""
        if values.get("ENVIRONMENT") == "production" and v == "your-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be changed in production environment")
        return v
    
    @validator("MAX_FILE_SIZE_MB")
    def validate_file_size(cls, v):
        """Validate file size limit."""
        if v < 1 or v > 100:
            raise ValueError("MAX_FILE_SIZE_MB must be between 1 and 100")
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> list:
        """Get allowed extensions as list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings."""
    
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DB_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""
    
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    DB_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_PER_MINUTE: int = 30


class TestSettings(Settings):
    """Test environment settings."""
    
    DEBUG: bool = True
    ENVIRONMENT: str = "test"
    DATABASE_URL: str = "sqlite:///./test.db"
    ENABLE_AI_PROCESSING: bool = False  # Disable AI in tests


def get_settings() -> Settings:
    """
    Get settings based on environment.
    
    Returns:
        Settings instance for current environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()

# Export
__all__ = ["settings", "Settings", "get_settings"]
