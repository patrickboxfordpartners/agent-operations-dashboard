"""Configuration for Mercury Intelligence"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # Mercury API
    MERCURY_API_KEY: str = os.getenv("MERCURY_API_KEY", "")
    MERCURY_WEBHOOK_SECRET: str = os.getenv("MERCURY_WEBHOOK_SECRET", "")
    MERCURY_ACCOUNT_ID: str = os.getenv("MERCURY_ACCOUNT_ID", "")

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL: str = "claude-sonnet-4-6"

    # Accounting integration
    QUICKBOOKS_ENABLED: bool = os.getenv("QUICKBOOKS_ENABLED", "false").lower() == "true"
    XERO_ENABLED: bool = os.getenv("XERO_ENABLED", "false").lower() == "true"

    # Categorization
    MIN_CONFIDENCE_AUTO_POST: float = 0.85
    MIN_CONFIDENCE_SUGGEST: float = 0.60

    # Recurring detection
    MIN_OCCURRENCES_FOR_RECURRING: int = 3  # Need to see 3x before flagging as recurring
    RECURRING_AMOUNT_TOLERANCE: float = 0.10  # 10% variance allowed

    # Anomaly detection
    ANOMALY_AMOUNT_THRESHOLD: float = 2.0  # 2x stddev = anomaly
    UNUSUAL_TIMING_WINDOW: int = 22  # Transactions outside 6am-10pm flagged

    # Client payment matching
    CLIENT_NAMES: list[str] = [
        # Will be populated from CRM or config
        # "Smith & Associates",
        # "Acme Corp",
    ]

    # Notifications
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")

    # Storage
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./mercury_intelligence.db")

    # Cost controls
    DAILY_SPEND_LIMIT: float = 20.0

config = Config()
