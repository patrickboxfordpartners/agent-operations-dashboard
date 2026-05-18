"""Data models for lead nurture system"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from datetime import datetime

class Lead(BaseModel):
    """Lead information"""
    lead_id: str
    name: str
    email: EmailStr
    company: Optional[str] = None
    vertical: Optional[str] = None
    company_size: Optional[str] = None
    source: Literal["website_form", "linkedin_dm", "email", "referral", "other"] = "other"

    # Initial message/context
    message: str
    pain_signals: list[str] = Field(default_factory=list)
    budget_signals: list[str] = Field(default_factory=list)
    urgency_signals: list[str] = Field(default_factory=list)

    # Timestamps
    received_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class LeadScore(BaseModel):
    """AI readiness score for a lead"""
    lead_id: str
    overall_score: int = Field(..., ge=1, le=10)

    # Dimension scores (0-10)
    pain_clarity: int = Field(..., ge=0, le=10)
    budget_likelihood: int = Field(..., ge=0, le=10)
    decision_authority: int = Field(..., ge=0, le=10)
    ai_readiness: int = Field(..., ge=0, le=10)
    urgency: int = Field(..., ge=0, le=10)

    # Analysis
    reasoning: str
    key_strengths: list[str]
    concerns: list[str]
    recommended_action: Literal["engage_immediately", "nurture_sequence", "qualify_further", "deprioritize"]

    # Personalization hints
    talking_points: list[str] = Field(default_factory=list)
    relevant_case_studies: list[str] = Field(default_factory=list)

    scored_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class EmailSequence(BaseModel):
    """Personalized email sequence for a lead"""
    lead_id: str
    sequence_type: Literal["high_intent", "qualification", "re_engagement"]

    emails: list[dict]  # Each: {subject, body, send_delay_hours, cta}

    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
