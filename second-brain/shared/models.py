"""Pydantic models for data validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime

# Taxonomy - extend as you encounter new verticals
VERTICALS = [
    "healthcare",
    "legal",
    "manufacturing",
    "retail",
    "saas",
    "services",
    "education",
    "real_estate",
    "other"
]

SOLUTION_CATEGORIES = [
    "workflow_automation",
    "data_analysis",
    "customer_service",
    "content_generation",
    "scheduling",
    "document_processing",
    "reporting",
    "other"
]

class ProjectMetadata(BaseModel):
    """Core project metadata"""

    # Required fields
    client_name: str = Field(..., min_length=1)
    vertical: Literal[tuple(VERTICALS)] = Field(...)  # type: ignore
    pain_point: str = Field(..., min_length=10)
    solution_description: str = Field(..., min_length=20)
    date_completed: str = Field(...)  # ISO 8601 format

    # Auto-extracted fields
    tools_used: list[str] = Field(default_factory=list)
    solution_category: Optional[str] = None
    roi_metric: Optional[str] = None
    cost_to_build: Optional[float] = None
    monthly_client_savings: Optional[float] = None
    project_duration_hours: Optional[float] = None

    # Quality scores
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reusability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    documentation_quality: float = Field(default=0.0, ge=0.0, le=1.0)

    # Metadata
    file_path: Optional[str] = None
    ingested_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('date_completed')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Ensure valid ISO 8601 date"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f"date_completed must be ISO 8601 format, got: {v}")

    @field_validator('roi_metric')
    @classmethod
    def validate_roi(cls, v: Optional[str]) -> Optional[str]:
        """Ensure ROI metric includes quantification"""
        if v and not any(x in v.lower() for x in ['%', 'hour', 'time', '$', 'cost', 'increase', 'reduction', 'saving']):
            raise ValueError("ROI metric must include quantified improvement")
        return v

class CompletenessAssessment(BaseModel):
    """Assessment of project documentation completeness"""

    completeness_score: float = Field(..., ge=0.0, le=1.0)
    missing_fields: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    can_auto_enrich: bool = False
    reasoning: str = ""

class QualityScores(BaseModel):
    """Quality dimension scores"""

    reusability_score: float = Field(..., ge=0.0, le=1.0)
    documentation_quality: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = ""

class DuplicateCheck(BaseModel):
    """Result of duplication check"""

    is_duplicate: bool
    existing_id: Optional[str] = None
    similarity: Optional[float] = None
    existing_project: Optional[dict] = None
    action: Optional[Literal["merge", "version", "separate"]] = None

class QueryResult(BaseModel):
    """Search result from vector DB"""

    id: str
    score: float
    metadata: dict

class RelevanceValidation(BaseModel):
    """Validation of query results"""

    relevance_scores: list[float]
    avg_relevance: float
    needs_refinement: bool
    suggested_refinement: Optional[str] = None
