"""Detect recurring charges and subscriptions"""
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from typing import Optional
import statistics

from shared.models import MercuryTransaction, RecurringCharge
from shared.config import config

class RecurringDetector:
    """Detects recurring charges from transaction history"""

    def __init__(self):
        self.patterns = {}  # merchant -> list of transactions
        self.detected_recurring = {}  # pattern_id -> RecurringCharge

    async def analyze_transaction(
        self,
        transaction: MercuryTransaction,
        historical_transactions: list[MercuryTransaction]
    ) -> Optional[RecurringCharge]:
        """
        Check if transaction is part of recurring pattern

        Args:
            transaction: New transaction to analyze
            historical_transactions: Past transactions to compare against

        Returns:
            RecurringCharge if pattern detected, None otherwise
        """

        merchant = self._normalize_merchant(
            transaction.counterparty_name or transaction.bank_description
        )

        # Find similar past transactions
        similar = [
            t for t in historical_transactions
            if self._normalize_merchant(t.counterparty_name or t.bank_description) == merchant
            and abs(float(t.amount) - float(transaction.amount)) / float(transaction.amount) < config.RECURRING_AMOUNT_TOLERANCE
        ]

        if len(similar) < config.MIN_OCCURRENCES_FOR_RECURRING - 1:
            # Not enough occurrences yet
            return None

        # Analyze pattern
        all_txns = similar + [transaction]
        all_txns.sort(key=lambda t: t.created_at)

        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(all_txns)):
            days = (all_txns[i].created_at - all_txns[i-1].created_at).days
            intervals.append(days)

        if not intervals:
            return None

        avg_interval = statistics.mean(intervals)
        interval_stddev = statistics.stdev(intervals) if len(intervals) > 1 else 0

        # Classify frequency
        frequency = self._classify_frequency(avg_interval)
        if not frequency:
            return None  # Too irregular

        # Calculate stats
        amounts = [float(t.amount) for t in all_txns]
        avg_amount = Decimal(str(statistics.mean(amounts)))
        amount_variance = Decimal(str(statistics.stdev(amounts))) if len(amounts) > 1 else Decimal("0")

        # Predict next occurrence
        next_expected = all_txns[-1].created_at + timedelta(days=int(avg_interval))

        # Calculate annual cost
        annual_multiplier = {
            "weekly": 52,
            "monthly": 12,
            "quarterly": 4,
            "annual": 1
        }
        annual_cost = avg_amount * annual_multiplier[frequency]

        # Build RecurringCharge
        recurring = RecurringCharge(
            id=f"rec_{merchant}_{frequency}",
            merchant=merchant,
            amount=avg_amount,
            frequency=frequency,
            next_expected_date=next_expected,
            first_seen=all_txns[0].created_at,
            last_seen=all_txns[-1].created_at,
            occurrence_count=len(all_txns),
            avg_amount=avg_amount,
            amount_variance=amount_variance,
            category="Subscription",  # Will be refined by categorizer
            confidence=self._calculate_confidence(interval_stddev, amount_variance, len(all_txns)),
            annual_cost=annual_cost
        )

        return recurring

    def _normalize_merchant(self, merchant: str) -> str:
        """Normalize merchant name for matching"""
        # Remove common suffixes
        merchant = merchant.upper()
        for suffix in ["INC", "LLC", "CORP", "LTD"]:
            merchant = merchant.replace(suffix, "")

        # Remove special chars
        merchant = "".join(c for c in merchant if c.isalnum() or c.isspace())

        return merchant.strip()

    def _classify_frequency(self, avg_interval_days: float) -> Optional[str]:
        """
        Classify frequency based on average interval

        Args:
            avg_interval_days: Average days between transactions

        Returns:
            Frequency string or None if too irregular
        """

        tolerance = 7  # days

        if abs(avg_interval_days - 7) <= tolerance:
            return "weekly"
        elif abs(avg_interval_days - 30) <= tolerance:
            return "monthly"
        elif abs(avg_interval_days - 90) <= tolerance * 2:
            return "quarterly"
        elif abs(avg_interval_days - 365) <= tolerance * 4:
            return "annual"
        else:
            return None  # Too irregular

    def _calculate_confidence(
        self,
        interval_stddev: float,
        amount_variance: Decimal,
        occurrence_count: int
    ) -> float:
        """
        Calculate confidence in recurring pattern

        Args:
            interval_stddev: Standard deviation of intervals
            amount_variance: Variance in amounts
            occurrence_count: Number of occurrences

        Returns:
            Confidence score 0-1
        """

        confidence = 1.0

        # Penalize high interval variance
        if interval_stddev > 7:
            confidence -= min(0.3, interval_stddev / 30)

        # Penalize high amount variance
        if float(amount_variance) > 5:
            confidence -= min(0.2, float(amount_variance) / 100)

        # Reward more occurrences
        if occurrence_count >= 6:
            confidence = min(1.0, confidence + 0.1)

        return max(0.0, min(1.0, confidence))

    def generate_insights(self, recurring_charges: list[RecurringCharge]) -> list[str]:
        """
        Generate insights about recurring charges

        Args:
            recurring_charges: List of detected recurring charges

        Returns:
            List of insight strings
        """

        insights = []

        if not recurring_charges:
            return insights

        # Total recurring cost
        total_monthly = sum(
            float(rc.amount) if rc.frequency == "monthly" else
            float(rc.amount) / 12 if rc.frequency == "annual" else
            float(rc.amount) * 4.33 if rc.frequency == "weekly" else
            float(rc.amount) / 3 if rc.frequency == "quarterly" else 0
            for rc in recurring_charges
        )

        insights.append(f"Total recurring monthly spend: ${total_monthly:,.2f} (${total_monthly * 12:,.2f}/year)")

        # Find highest cost
        highest = max(recurring_charges, key=lambda rc: rc.annual_cost)
        insights.append(f"Highest recurring cost: {highest.merchant} at ${float(highest.annual_cost):,.2f}/year")

        # Count by frequency
        freq_counts = {}
        for rc in recurring_charges:
            freq_counts[rc.frequency] = freq_counts.get(rc.frequency, 0) + 1

        insights.append(f"Frequency breakdown: {', '.join(f'{count} {freq}' for freq, count in freq_counts.items())}")

        # Flag if many subscriptions
        if len(recurring_charges) > 10:
            insights.append(f"⚠️ You have {len(recurring_charges)} recurring charges - consider auditing for unused subscriptions")

        return insights
