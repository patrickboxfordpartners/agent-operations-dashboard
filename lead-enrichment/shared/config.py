"""Configuration for lead enrichment"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL: str = "claude-sonnet-4-6"

    # Enrichment APIs
    CLEARBIT_API_KEY: str = os.getenv("CLEARBIT_API_KEY", "")
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")  # Email finder
    APOLLO_API_KEY: str = os.getenv("APOLLO_API_KEY", "")  # B2B database
    BUILTWITH_API_KEY: str = os.getenv("BUILTWITH_API_KEY", "")  # Tech stack
    CRUNCHBASE_API_KEY: str = os.getenv("CRUNCHBASE_API_KEY", "")  # Funding data

    # Social APIs
    LINKEDIN_API_KEY: str = os.getenv("LINKEDIN_API_KEY", "")

    # ICP Criteria (Ideal Customer Profile)
    TARGET_EMPLOYEE_RANGE: tuple[int, int] = (10, 500)  # 10-500 employees
    TARGET_REVENUE_RANGE: tuple[int, int] = (1_000_000, 50_000_000)  # $1M-$50M
    TARGET_INDUSTRIES: list[str] = [
        "Professional Services",
        "Healthcare",
        "Legal Services",
        "Financial Services",
        "Real Estate"
    ]
    TARGET_TECHNOLOGIES: list[str] = [
        "Salesforce",
        "HubSpot",
        "QuickBooks",
        "Xero",
        "Slack",
        "Microsoft 365"
    ]
    TARGET_TITLES: list[str] = [
        "CEO", "COO", "CFO",
        "VP Operations", "Director of Operations",
        "Office Manager", "Practice Manager"
    ]

    # Scoring weights (must sum to 1.0)
    WEIGHT_ICP_FIT: float = 0.40
    WEIGHT_BUYING_SIGNALS: float = 0.35
    WEIGHT_CONTACT_QUALITY: float = 0.25

    # Cost controls
    DAILY_SPEND_LIMIT: float = 100.0
    MAX_LEADS_PER_RUN: int = 100

    # Second Brain integration
    SECOND_BRAIN_ENABLED: bool = os.getenv("SECOND_BRAIN_ENABLED", "false").lower() == "true"

config = Config()
