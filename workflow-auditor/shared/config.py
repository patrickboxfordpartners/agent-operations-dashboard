"""Configuration for Workflow Auditor"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")

    # Notion
    NOTION_AUDITS_DATABASE_ID: str = os.getenv("NOTION_AUDITS_DATABASE_ID", "")

    # Second Brain Integration
    SECOND_BRAIN_PATH: Path = Path(os.getenv("SECOND_BRAIN_PATH", "../second-brain"))

    # Server
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Cost Controls
    DAILY_SPEND_LIMIT: float = float(os.getenv("DAILY_SPEND_LIMIT", "200.0"))

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required config values"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")
        if not cls.NOTION_TOKEN:
            errors.append("NOTION_TOKEN is required (get from notion.so/my-integrations)")
        if not cls.NOTION_AUDITS_DATABASE_ID:
            errors.append("NOTION_AUDITS_DATABASE_ID is required")

        return errors

config = Config()
