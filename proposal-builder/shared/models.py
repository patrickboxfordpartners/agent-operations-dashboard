"""Data models for proposal builder"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional, Union
from datetime import datetime
from decimal import Decimal

# Service Types
ServiceType = Literal["ai_automation", "web_development", "combined"]

# Input Data Models

class ClientInfo(BaseModel):
    """Basic client information"""
    company_name: str
    contact_name: str
    contact_email: EmailStr
    industry: Optional[str] = None
    company_size: Optional[int] = None
    website: Optional[str] = None

class DiscoveryNotes(BaseModel):
    """Notes from discovery call or intake form"""
    pain_points: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    budget_range: Optional[str] = None
    timeline_urgency: Optional[str] = None
    decision_makers: list[str] = Field(default_factory=list)
    current_tools: list[str] = Field(default_factory=list)
    notes: str = ""

class AutomationInputs(BaseModel):
    """Inputs for AI automation proposals"""
    workflow_analysis: Optional[dict] = None  # From Workflow Auditor
    workflow_solutions: Optional[dict] = None  # From Solution Generator
    lead_enrichment: Optional[dict] = None  # From Lead Enrichment
    pain_points: Optional[dict] = None  # From Pain Scanner

class WebDevInputs(BaseModel):
    """Inputs for web development proposals"""
    site_analysis: Optional[dict] = None  # From website analyzer
    current_tech_stack: list[str] = Field(default_factory=list)
    seo_issues: list[str] = Field(default_factory=list)
    performance_issues: list[str] = Field(default_factory=list)
    design_requirements: Optional[str] = None

# Proposal Components

class Phase(BaseModel):
    """Implementation phase"""
    name: str
    description: str
    deliverables: list[str]
    timeline: str
    dependencies: list[str] = Field(default_factory=list)

class PricingTier(BaseModel):
    """Pricing option"""
    name: str
    subtitle: str
    price_range: str
    price_min: Decimal
    price_max: Decimal
    timeline: str
    description: str
    included: list[str]
    excluded: list[str] = Field(default_factory=list)
    recommended: bool = False

class ROIProjection(BaseModel):
    """ROI calculation"""
    time_saved_per_week: float
    cost_savings_annual: Decimal
    revenue_impact_annual: Decimal
    payback_months: float
    three_year_roi: Decimal

class CaseStudy(BaseModel):
    """Relevant case study"""
    client_name: str
    industry: str
    challenge: str
    solution: str
    results: list[str]

# Final Proposal

class Proposal(BaseModel):
    """Complete proposal document"""

    # Metadata
    proposal_id: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    service_type: ServiceType

    # Client info
    client: ClientInfo

    # Cover
    title: str
    subtitle: str

    # Executive Summary
    executive_summary: str

    # Current State
    current_state_overview: str
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)

    # Proposed Solution
    solution_overview: str
    phases: list[Phase]

    # Pricing
    pricing_tiers: list[PricingTier]
    payment_terms: str

    # Value Proposition
    why_us: list[str]
    case_studies: list[CaseStudy] = Field(default_factory=list)
    roi_projection: Optional[ROIProjection] = None

    # Next Steps
    next_steps: list[str]
    expiration_date: Optional[str] = None

    # Terms
    assumptions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)

class ProposalRequest(BaseModel):
    """Request to generate a proposal"""
    service_type: ServiceType
    client: ClientInfo
    discovery: DiscoveryNotes

    # Service-specific inputs
    automation_inputs: Optional[AutomationInputs] = None
    webdev_inputs: Optional[WebDevInputs] = None

    # Customization
    brand_name: str = "Boxford Partners"
    include_case_studies: bool = True
    include_roi: bool = True
    tone: Literal["professional", "friendly", "technical"] = "professional"

class ProposalStats(BaseModel):
    """Statistics for proposal generation"""
    total_generated: int
    by_service_type: dict[str, int]
    avg_generation_time: float
    avg_cost: float
