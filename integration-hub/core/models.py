"""Core data models for Integration Hub"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# ENTITY MODELS (canonical representations)
# ============================================================================

class EntityType(str, Enum):
    """Types of entities in the system"""
    LEAD = "lead"
    CLIENT = "client"
    PROJECT = "project"
    PROPOSAL = "proposal"
    INVOICE = "invoice"
    TRANSACTION = "transaction"
    CONTENT = "content"
    WORKFLOW = "workflow"

class LeadStatus(str, Enum):
    """Lead lifecycle stages"""
    NEW = "new"
    ENRICHED = "enriched"
    QUALIFIED = "qualified"
    WORKFLOW_ANALYZED = "workflow_analyzed"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"

class Lead(BaseModel):
    """Canonical lead entity"""
    id: str
    status: LeadStatus

    # Basic info
    email: EmailStr
    name: str
    company: str
    title: Optional[str] = None

    # Source tracking
    source: str  # "form", "linkedin", "content", "referral"
    source_detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Enrichment data (from Lead Enrichment system)
    enrichment_score: Optional[int] = None
    enrichment_grade: Optional[str] = None
    enrichment_data: Optional[dict] = None

    # Workflow data (from Workflow Auditor)
    workflow_analysis_id: Optional[str] = None
    workflow_data: Optional[dict] = None

    # Proposal data
    proposal_id: Optional[str] = None
    proposal_sent_at: Optional[datetime] = None
    proposal_viewed_at: Optional[datetime] = None
    proposal_opened_count: int = 0

    # Engagement tracking
    last_contact: Optional[datetime] = None
    next_followup: Optional[datetime] = None
    nurture_sequence_id: Optional[str] = None

    # System references
    system_ids: dict[str, str] = Field(default_factory=dict)  # {system_name: system_id}

class Client(BaseModel):
    """Canonical client entity (converted from Lead)"""
    id: str
    lead_id: str  # Original lead ID

    # Basic info
    email: EmailStr
    name: str
    company: str

    # Contract info
    contract_value: float
    contract_signed_at: datetime
    project_start_date: Optional[datetime] = None

    # Payment tracking
    invoices: list[str] = Field(default_factory=list)  # Invoice IDs
    payments_received: float = 0.0
    payments_pending: float = 0.0

    # Project tracking
    active_projects: list[str] = Field(default_factory=list)

    # System references
    system_ids: dict[str, str] = Field(default_factory=dict)

class Project(BaseModel):
    """Active client project"""
    id: str
    client_id: str

    name: str
    description: str

    # Timeline
    start_date: datetime
    end_date: Optional[datetime] = None
    status: Literal["planning", "active", "paused", "completed", "cancelled"]

    # Financials
    total_value: float
    paid: float
    remaining: float

    # Deliverables
    phases: list[dict] = Field(default_factory=list)
    milestones: list[dict] = Field(default_factory=list)

class Transaction(BaseModel):
    """Financial transaction (from Mercury)"""
    id: str
    date: datetime
    amount: float
    description: str
    merchant: Optional[str] = None

    # Categorization
    category: str
    confidence: float

    # Matching
    client_id: Optional[str] = None
    invoice_id: Optional[str] = None
    project_id: Optional[str] = None

    # Flags
    is_client_payment: bool = False
    is_recurring: bool = False
    needs_review: bool = False

# ============================================================================
# EVENT MODELS (system communications)
# ============================================================================

class EventType(str, Enum):
    """Types of events that flow through the hub"""
    # Lead events
    LEAD_CREATED = "lead.created"
    LEAD_ENRICHED = "lead.enriched"
    LEAD_QUALIFIED = "lead.qualified"
    LEAD_WON = "lead.won"
    LEAD_LOST = "lead.lost"

    # Workflow events
    WORKFLOW_ANALYZED = "workflow.analyzed"
    WORKFLOW_SOLUTION_GENERATED = "workflow.solution_generated"

    # Proposal events
    PROPOSAL_GENERATED = "proposal.generated"
    PROPOSAL_SENT = "proposal.sent"
    PROPOSAL_VIEWED = "proposal.viewed"
    PROPOSAL_ACCEPTED = "proposal.accepted"

    # Payment events
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_MATCHED = "payment.matched"
    INVOICE_PAID = "invoice.paid"

    # Anomaly events
    ANOMALY_DETECTED = "anomaly.detected"
    RECURRING_CHARGE_DETECTED = "recurring.detected"

    # Content events
    CONTENT_PUBLISHED = "content.published"
    PAIN_POINT_DISCOVERED = "pain.discovered"

class Event(BaseModel):
    """Event that flows through the integration hub"""
    id: str = Field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.now)

    # Source system
    source_system: str  # "lead-enrichment", "mercury-intelligence", etc
    source_entity_id: str

    # Canonical entity (if applicable)
    entity_type: Optional[EntityType] = None
    entity_id: Optional[str] = None

    # Event payload
    data: dict[str, Any]

    # Processing
    processed: bool = False
    processed_at: Optional[datetime] = None
    error: Optional[str] = None

# ============================================================================
# WORKFLOW MODELS (automation flows)
# ============================================================================

class WorkflowType(str, Enum):
    """Pre-built workflow types"""
    LEAD_TO_PROPOSAL = "lead_to_proposal"
    PROPOSAL_TO_CLIENT = "proposal_to_client"
    PAYMENT_TO_ACCOUNTING = "payment_to_accounting"
    PAIN_TO_CONTENT = "pain_to_content"
    CONTENT_TO_LEAD = "content_to_lead"

class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    id: str
    name: str
    system: str  # Which system handles this step
    action: str  # What action to perform
    config: dict = Field(default_factory=dict)
    condition: Optional[str] = None  # Conditional logic

class Workflow(BaseModel):
    """Automated workflow definition"""
    id: str
    name: str
    type: WorkflowType
    description: str

    # Flow
    steps: list[WorkflowStep]
    triggers: list[EventType]

    # State
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class WorkflowExecution(BaseModel):
    """Running instance of a workflow"""
    id: str
    workflow_id: str
    trigger_event_id: str

    # State
    status: Literal["running", "completed", "failed", "paused"]
    current_step: int = 0
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Results
    step_results: list[dict] = Field(default_factory=list)
    error: Optional[str] = None

# ============================================================================
# INTEGRATION MODELS (system connectors)
# ============================================================================

class SystemStatus(BaseModel):
    """Health status of connected system"""
    system_name: str
    status: Literal["online", "offline", "error"]
    last_ping: datetime
    error_message: Optional[str] = None

class SyncConfig(BaseModel):
    """Configuration for system sync"""
    system_name: str
    entity_type: EntityType
    sync_direction: Literal["pull", "push", "bidirectional"]
    sync_frequency: int  # seconds
    last_sync: Optional[datetime] = None
    enabled: bool = True
