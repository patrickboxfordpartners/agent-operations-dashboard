"""Configuration for Integration Hub"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Central configuration"""

    # Hub settings
    HUB_NAME: str = "Integration Hub"
    HUB_VERSION: str = "0.1.0"

    # Storage
    DATABASE_PATH: str = os.getenv("HUB_DATABASE_PATH", "./integration_hub.db")
    EVENT_LOG_PATH: str = os.getenv("HUB_EVENT_LOG_PATH", "./events.log")

    # System paths (relative to project root)
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    SYSTEMS = {
        "second-brain": PROJECT_ROOT / "second-brain",
        "workflow-auditor": PROJECT_ROOT / "workflow-auditor",
        "lead-nurture": PROJECT_ROOT / "lead-nurture",
        "pain-scanner": PROJECT_ROOT / "pain-scanner",
        "content-engine": PROJECT_ROOT / "content-engine",
        "transaction-categorizer": PROJECT_ROOT / "transaction-categorizer",
        "lead-enrichment": PROJECT_ROOT / "lead-enrichment",
        "proposal-builder": PROJECT_ROOT / "proposal-builder",
        "mercury-intelligence": PROJECT_ROOT / "mercury-intelligence"
    }

    # API settings
    API_HOST: str = os.getenv("HUB_API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("HUB_API_PORT", "8080"))

    # Event processing
    EVENT_QUEUE_SIZE: int = 1000
    EVENT_BATCH_SIZE: int = 10
    EVENT_PROCESSING_INTERVAL: int = 1  # seconds

    # Workflow settings
    MAX_CONCURRENT_WORKFLOWS: int = 10
    WORKFLOW_TIMEOUT: int = 3600  # seconds

    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds

    # Monitoring
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    METRIC_RETENTION_DAYS: int = 90

    # Notifications
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")

config = Config()
