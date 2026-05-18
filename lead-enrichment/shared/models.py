"""Data models for lead enrichment"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from datetime import datetime

class RawLead(BaseModel):
    """Minimal lead info (what you start with)"""
    id: str
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None

    # Source tracking
    source: str = "unknown"  # form, linkedin, referral, etc
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class CompanyData(BaseModel):
    """Enriched company information"""
    name: str
    domain: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    employee_range: Optional[str] = None  # "1-10", "11-50", etc
    annual_revenue: Optional[int] = None
    revenue_range: Optional[str] = None
    founded_year: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None

    # Tech stack (from BuiltWith, Wappalyzer, etc)
    technologies: list[str] = Field(default_factory=list)
    tech_categories: dict[str, list[str]] = Field(default_factory=dict)

    # Funding (from Crunchbase)
    funding_stage: Optional[str] = None  # seed, series_a, etc
    total_funding: Optional[int] = None
    last_funding_date: Optional[str] = None

    # Social presence
    linkedin_url: Optional[str] = None
    linkedin_followers: Optional[int] = None
    twitter_handle: Optional[str] = None

class PersonData(BaseModel):
    """Enriched person information"""
    full_name: str
    email: EmailStr
    title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None  # entry, mid, senior, c_level

    # Contact info
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    phone: Optional[str] = None

    # Professional history
    years_in_role: Optional[int] = None
    years_at_company: Optional[int] = None
    previous_companies: list[str] = Field(default_factory=list)

class EnrichmentScore(BaseModel):
    """Scoring dimensions for a lead"""

    # ICP Fit (0-100)
    company_size_fit: int = 0  # Right employee count?
    industry_fit: int = 0  # Target industry?
    tech_stack_fit: int = 0  # Using relevant technologies?
    revenue_fit: int = 0  # Can afford your service?

    # Buying signals (0-100)
    funding_signal: int = 0  # Recent funding = budget
    growth_signal: int = 0  # Hiring = growing pains
    tech_debt_signal: int = 0  # Old tech = need to modernize

    # Contact quality (0-100)
    decision_maker_score: int = 0  # Right level/department?
    contact_findability: int = 0  # Easy to reach?
    engagement_potential: int = 0  # Active on socials?

    # Overall (weighted average)
    overall_score: int = 0  # 0-100
    grade: Literal["A", "B", "C", "D", "F"] = "F"

class EnrichedLead(BaseModel):
    """Fully enriched lead with score"""
    raw_lead: RawLead
    company: Optional[CompanyData] = None
    person: PersonData
    score: EnrichmentScore

    # AI-generated insights
    key_insights: list[str] = Field(default_factory=list)
    recommended_approach: str = ""
    talking_points: list[str] = Field(default_factory=list)

    # Enrichment metadata
    enrichment_confidence: float = 0.0  # 0-1, how confident in the data
    data_sources: list[str] = Field(default_factory=list)
    enriched_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    cost_usd: float = 0.0

class EnrichmentStats(BaseModel):
    """Statistics for enrichment run"""
    total_leads: int
    enriched: int
    failed: int

    # Score distribution
    grade_a: int = 0
    grade_b: int = 0
    grade_c: int = 0
    grade_d: int = 0
    grade_f: int = 0

    # Enrichment quality
    avg_confidence: float = 0.0
    company_data_found: int = 0
    tech_stack_found: int = 0
    funding_data_found: int = 0

    # Cost
    total_cost_usd: float = 0.0
    avg_cost_per_lead: float = 0.0
    duration_seconds: float = 0.0
