"""Configuration for transaction categorizer"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL: str = "claude-sonnet-4-6"

    # Accounting software (choose one)
    QUICKBOOKS_CLIENT_ID: str = os.getenv("QUICKBOOKS_CLIENT_ID", "")
    QUICKBOOKS_CLIENT_SECRET: str = os.getenv("QUICKBOOKS_CLIENT_SECRET", "")
    QUICKBOOKS_REALM_ID: str = os.getenv("QUICKBOOKS_REALM_ID", "")

    XERO_CLIENT_ID: str = os.getenv("XERO_CLIENT_ID", "")
    XERO_CLIENT_SECRET: str = os.getenv("XERO_CLIENT_SECRET", "")

    # Bank feeds
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")  # sandbox, development, production

    # Quality thresholds
    MIN_CONFIDENCE_AUTO_POST: float = 0.85  # Auto-post if >= this
    MIN_CONFIDENCE_SUGGEST: float = 0.60    # Suggest if >= this
    SIMILARITY_THRESHOLD: float = 0.90      # For duplicate detection

    # Cost controls
    DAILY_SPEND_LIMIT: float = 50.0
    MAX_TRANSACTIONS_PER_RUN: int = 500

    # Second Brain integration
    SECOND_BRAIN_ENABLED: bool = os.getenv("SECOND_BRAIN_ENABLED", "false").lower() == "true"

config = Config()
