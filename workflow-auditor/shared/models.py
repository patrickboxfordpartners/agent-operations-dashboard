"""Pydantic models for workflow auditor"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ClientInfo(BaseModel):
    """Client information"""
    name: str
    email: str
    vertical: str
    company_size: str = Field(default="unknown")
    urgency: Literal["low", "medium", "high"] = "medium"

class AuditInput(BaseModel):
    """Input for audit generation"""
    audit_id: str
    client: ClientInfo
    input_type: Literal["loom_video", "google_doc", "text"]
    content: str  # URL for video/doc, raw text otherwise
    received_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    step_number: int
    action: str
    performed_by: str
    tool: str
    avg_duration_minutes: float
    pain_points: list[str]
    automation_potential: Literal["low", "medium", "high", "very_high"]

class WorkflowAnalysis(BaseModel):
    """Structured workflow analysis"""
    workflow_name: str
    frequency: str
    total_time_per_cycle: float
    people_involved: list[str]
    steps: list[WorkflowStep]
    current_cost: dict  # annual_cost, weekly_hours, etc.

class Solution(BaseModel):
    """An automation solution"""
    name: str
    description: str
    automation_level: float  # 0.0-1.0
    architecture: dict
    tools: list[str]
    estimated_outcomes: dict
    build_cost: dict
    monthly_tool_cost: float
    risks: list[str]
    timeline_weeks: int

class AuditOutput(BaseModel):
    """Complete audit output"""
    audit_id: str
    client_name: str
    vertical: str
    workflow: WorkflowAnalysis
    solutions: dict[str, Solution]  # solution_1_conservative, etc.
    recommended_solution: str
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
