"""Configuration management"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration"""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    VOYAGE_API_KEY: str = os.getenv("VOYAGE_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")

    # Pinecone
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-west-2")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "second-brain")

    # Langfuse
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    # Paths
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", "~/completed-work")).expanduser()
    KNOWLEDGE_GRAPH_PATH: Path = Path(os.getenv("KNOWLEDGE_GRAPH_PATH", "./storage/knowledge_graph.json"))

    # Quality Thresholds
    MIN_COMPLETENESS_SCORE: float = float(os.getenv("MIN_COMPLETENESS_SCORE", "0.7"))
    MIN_DOCUMENTATION_QUALITY: float = float(os.getenv("MIN_DOCUMENTATION_QUALITY", "0.5"))
    DEDUP_SIMILARITY_THRESHOLD: float = float(os.getenv("DEDUP_SIMILARITY_THRESHOLD", "0.85"))

    # Cost Controls
    DAILY_SPEND_LIMIT: float = float(os.getenv("DAILY_SPEND_LIMIT", "100.0"))
    ALERT_THRESHOLD: float = float(os.getenv("ALERT_THRESHOLD", "0.8"))

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Pricing (per 1M tokens)
    PRICING = {
        "claude-opus-4-7": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5": {"input": 0.8, "output": 4.0},
        "voyage-2": 0.12  # per 1M tokens
    }

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required config values"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")
        if not cls.VOYAGE_API_KEY:
            errors.append("VOYAGE_API_KEY is required")
        if not cls.PINECONE_API_KEY:
            errors.append("PINECONE_API_KEY is required")

        return errors

config = Config()
