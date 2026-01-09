"""
Application Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "PropelSense API"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins"""
        return [
            self.FRONTEND_URL,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


# Create settings instance
settings = Settings()
