"""Configuration for proposal builder"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL: str = "claude-sonnet-4-6"

    # Brand defaults
    DEFAULT_BRAND_NAME: str = "Boxford Partners"
    DEFAULT_TAGLINE: str = "Technology Consulting & AI Automation"
    DEFAULT_WEBSITE: str = "https://boxfordpartners.com"
    DEFAULT_LOGO_PATH: str = ""

    # Pricing guidelines (used by AI to suggest tiers)
    PRICING_RANGES = {
        "ai_automation": {
            "small": (5_000, 15_000),
            "medium": (15_000, 35_000),
            "large": (35_000, 75_000),
            "enterprise": (75_000, 200_000)
        },
        "web_development": {
            "simple": (3_000, 8_000),
            "standard": (8_000, 20_000),
            "advanced": (20_000, 50_000),
            "enterprise": (50_000, 150_000)
        },
        "combined": {
            "starter": (10_000, 25_000),
            "growth": (25_000, 60_000),
            "transform": (60_000, 150_000),
            "enterprise": (150_000, 300_000)
        }
    }

    # Document generation
    PROPOSAL_EXPIRATION_DAYS: int = 30
    PDF_GENERATION_ENABLED: bool = False  # Requires reportlab or weasyprint

    # Integration paths (relative to project root)
    WORKFLOW_AUDITOR_PATH: str = "../workflow-auditor"
    LEAD_ENRICHMENT_PATH: str = "../lead-enrichment"
    SECOND_BRAIN_PATH: str = "../second-brain"

    # Cost controls
    DAILY_SPEND_LIMIT: float = 50.0

config = Config()
