"""Data models for Mercury Intelligence"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from decimal import Decimal

class MercuryTransaction(BaseModel):
    """Transaction from Mercury webhook or API"""
    id: str
    status: Literal["pending", "sent", "cancelled", "failed"]
    amount: Decimal
    bank_description: str
    counterparty_name: Optional[str] = None
    counterparty_id: Optional[str] = None
    created_at: datetime
    posted_at: Optional[datetime] = None

    # Mercury-specific
    kind: Literal["incomingDomesticWire", "incomingInternationalWire",
                  "outgoingDomesticWire", "outgoingInternationalWire",
                  "outgoingCheck", "debitCardTransaction", "incomingAch",
                  "outgoingAch", "fee", "other"]

    note: Optional[str] = None
    has_receipt: bool = False

    # Account info
    account_id: str

class CategorizedTransaction(BaseModel):
    """Mercury transaction with AI categorization"""
    transaction: MercuryTransaction

    # Categorization
    category_id: str
    category_name: str
    confidence: float
    reasoning: str

    # Flags
    needs_review: bool = False
    is_recurring: bool = False
    is_client_payment: bool = False
    is_anomaly: bool = False

    # Context
    matched_client: Optional[str] = None
    matched_invoice: Optional[str] = None
    recurring_pattern_id: Optional[str] = None

    categorized_at: datetime = Field(default_factory=datetime.now)

class RecurringCharge(BaseModel):
    """Detected recurring charge/subscription"""
    id: str
    merchant: str
    amount: Decimal
    frequency: Literal["weekly", "monthly", "quarterly", "annual"]
    next_expected_date: datetime

    # Pattern
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    avg_amount: Decimal
    amount_variance: Decimal  # Stddev

    # Classification
    category: str
    is_active: bool = True
    confidence: float

    # Analysis
    annual_cost: Decimal
    notes: list[str] = Field(default_factory=list)

class SpendAnalysis(BaseModel):
    """Spending analysis for period"""
    period_start: datetime
    period_end: datetime

    # Totals
    total_spend: Decimal
    total_income: Decimal
    net: Decimal

    # By category
    spend_by_category: dict[str, Decimal]

    # Recurring
    recurring_monthly: Decimal
    recurring_annual: Decimal
    recurring_charges: list[RecurringCharge]

    # Top vendors
    top_vendors: list[dict]  # [{vendor, amount, count}]

    # Insights
    insights: list[str]
    warnings: list[str]

class Anomaly(BaseModel):
    """Detected anomalous transaction"""
    transaction: MercuryTransaction
    anomaly_type: Literal["unusual_amount", "unusual_merchant", "unusual_timing",
                          "duplicate_possible", "frequency_spike"]
    severity: Literal["info", "warning", "critical"]

    reason: str
    expected_value: Optional[str] = None
    actual_value: str

    detected_at: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = False

class ClientPayment(BaseModel):
    """Detected client payment"""
    transaction: MercuryTransaction

    # Matching
    client_name: str
    confidence: float
    matched_invoice_id: Optional[str] = None

    # Context
    project_id: Optional[str] = None
    expected_amount: Optional[Decimal] = None
    amount_variance: Optional[Decimal] = None

    # Actions
    notification_sent: bool = False
    accounting_posted: bool = False
    thank_you_sent: bool = False

class WebhookEvent(BaseModel):
    """Mercury webhook event wrapper"""
    event_type: Literal["transaction.created", "transaction.updated"]
    transaction: MercuryTransaction
    received_at: datetime = Field(default_factory=datetime.now)
    processed: bool = False
    error: Optional[str] = None

class IntelligenceStats(BaseModel):
    """Statistics for Mercury Intelligence"""
    total_transactions: int
    categorized: int
    client_payments_detected: int
    recurring_charges_found: int
    anomalies_detected: int

    avg_categorization_time: float
    avg_confidence: float

    period_start: datetime
    period_end: datetime
