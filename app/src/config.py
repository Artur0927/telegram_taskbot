"""
Configuration module - loads environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "80"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required environment variables."""
        missing = []
        if not cls.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.WEBHOOK_URL:
            missing.append("WEBHOOK_URL")
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")


config = Config()
