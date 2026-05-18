"""Data models for pain scanner"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class PainPoint(BaseModel):
    """A discovered pain point"""
    pain_id: str
    vertical: str
    source: Literal["reddit", "rss", "forum", "x"]
    source_url: str

    # The pain
    title: str
    description: str
    evidence_quotes: list[str]  # Direct quotes showing the pain

    # Analysis
    frequency: Literal["isolated", "uncommon", "common", "widespread"]
    urgency: Literal["low", "medium", "high", "critical"]
    estimated_market_size: str  # "100s", "1000s", "10,000+"

    # Solution
    proposed_solution: str
    estimated_build_time: str  # "1-2 weeks", "3-4 weeks", etc.
    estimated_roi: str

    # Metadata
    discovered_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class VerticalConfig(BaseModel):
    """Configuration for monitoring a vertical"""
    vertical: str
    reddit_subreddits: list[str] = Field(default_factory=list)
    rss_feeds: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
