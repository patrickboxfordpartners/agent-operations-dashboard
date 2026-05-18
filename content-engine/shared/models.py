"""Data models for content engine"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ContentRequest(BaseModel):
    """Request for content generation"""
    content_type: Literal["linkedin_post", "twitter_thread", "blog_post", "email_newsletter"]
    topic: str
    key_points: list[str] = Field(default_factory=list)
    target_audience: str = "small business owners"
    tone: Literal["professional", "casual", "technical", "friendly"] = "professional"

    # Source material (optional)
    case_study_id: Optional[str] = None  # From Second Brain
    pain_point_id: Optional[str] = None  # From Pain Scanner

class GeneratedContent(BaseModel):
    """Generated content piece"""
    content_type: str
    title: Optional[str] = None
    body: str
    metadata: dict = Field(default_factory=dict)  # hashtags, CTAs, etc.
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
