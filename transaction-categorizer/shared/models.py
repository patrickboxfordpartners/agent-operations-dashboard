"""Data models for transaction categorizer"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from decimal import Decimal

class Transaction(BaseModel):
    """Raw transaction from bank feed"""
    id: str
    date: datetime
    amount: Decimal
    description: str
    merchant: Optional[str] = None
    account_id: str
    account_type: Literal["checking", "savings", "credit_card"]

    # Optional metadata from Plaid
    category_plaid: Optional[list[str]] = None
    merchant_name: Optional[str] = None
    payment_channel: Optional[str] = None  # online, in store, etc

class Category(BaseModel):
    """Accounting category"""
    id: str
    name: str
    account_type: Literal["expense", "income", "asset", "liability", "equity"]
    parent_id: Optional[str] = None
    tax_category: Optional[str] = None

    # Business rules
    keywords: list[str] = Field(default_factory=list)
    merchant_patterns: list[str] = Field(default_factory=list)
    amount_range: Optional[tuple[float, float]] = None

class CategorizedTransaction(BaseModel):
    """Transaction with AI-assigned category"""
    transaction: Transaction
    category_id: str
    category_name: str
    confidence: float  # 0-1
    reasoning: str

    # Reconciliation
    needs_review: bool = False
    review_reason: Optional[str] = None

    # Similar past transactions (for learning)
    similar_count: int = 0
    historical_category: Optional[str] = None

    categorized_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class ReconciliationResult(BaseModel):
    """Result of reconciling with accounting software"""
    transaction_id: str
    status: Literal["matched", "new", "duplicate", "conflict"]

    # If matched
    accounting_software_id: Optional[str] = None
    matches: list[dict] = Field(default_factory=list)

    # If conflict
    conflict_reason: Optional[str] = None
    suggested_action: Optional[str] = None

    reconciled_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class CategorizationStats(BaseModel):
    """Statistics for a categorization run"""
    total_transactions: int
    categorized: int
    needs_review: int
    high_confidence: int  # confidence > 0.8
    duplicates_found: int
    conflicts_found: int

    cost_usd: float
    duration_seconds: float

    categories_used: dict[str, int]  # category -> count
