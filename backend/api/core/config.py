import os
from typing import List
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Smart Contract Intelligence Platform"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/smart_contracts")

    # AI Service
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Blockchain Service
    BLOCKCHAIN_SERVICE_URL: str = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://localhost:8080")
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/your-infura-key")
    ETH_CHAIN_ID: int = int(os.getenv("ETH_CHAIN_ID", "1"))  # Mainnet by default

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()