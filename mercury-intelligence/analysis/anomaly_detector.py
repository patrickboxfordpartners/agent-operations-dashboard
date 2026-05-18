"""Detect anomalous transactions"""
import statistics
from datetime import datetime, time
from typing import Optional
from decimal import Decimal

from shared.models import MercuryTransaction, Anomaly
from shared.config import config

class AnomalyDetector:
    """Detects unusual transactions"""

    def __init__(self):
        pass

    async def check_transaction(
        self,
        transaction: MercuryTransaction,
        historical_transactions: list[MercuryTransaction]
    ) -> Optional[Anomaly]:
        """
        Check if transaction is anomalous

        Args:
            transaction: Transaction to check
            historical_transactions: Historical context

        Returns:
            Anomaly if detected, None otherwise
        """

        # Check unusual amount
        anomaly = self._check_unusual_amount(transaction, historical_transactions)
        if anomaly:
            return anomaly

        # Check unusual merchant
        anomaly = self._check_unusual_merchant(transaction, historical_transactions)
        if anomaly:
            return anomaly

        # Check unusual timing
        anomaly = self._check_unusual_timing(transaction)
        if anomaly:
            return anomaly

        # Check possible duplicate
        anomaly = self._check_duplicate(transaction, historical_transactions)
        if anomaly:
            return anomaly

        return None

    def _check_unusual_amount(
        self,
        transaction: MercuryTransaction,
        historical: list[MercuryTransaction]
    ) -> Optional[Anomaly]:
        """Check if amount is unusually large"""

        if not historical or len(historical) < 10:
            # Not enough history
            return None

        # Get similar transactions (same merchant or similar description)
        merchant = transaction.counterparty_name or transaction.bank_description
        similar = [
            t for t in historical
            if (t.counterparty_name == transaction.counterparty_name)
            or (merchant.lower() in t.bank_description.lower())
        ]

        if not similar or len(similar) < 3:
            # Check against all transactions
            amounts = [float(t.amount) for t in historical]
        else:
            # Check against similar transactions
            amounts = [float(t.amount) for t in similar]

        if len(amounts) < 3:
            return None

        mean = statistics.mean(amounts)
        stddev = statistics.stdev(amounts)

        # Check if current transaction is > 2 stddev above mean
        if float(transaction.amount) > mean + (config.ANOMALY_AMOUNT_THRESHOLD * stddev):
            severity = "critical" if float(transaction.amount) > mean + (3 * stddev) else "warning"

            return Anomaly(
                transaction=transaction,
                anomaly_type="unusual_amount",
                severity=severity,
                reason=f"Amount ${transaction.amount} is {((float(transaction.amount) - mean) / stddev):.1f}x standard deviations above typical",
                expected_value=f"~${mean:.2f} (typical)",
                actual_value=f"${transaction.amount}"
            )

        return None

    def _check_unusual_merchant(
        self,
        transaction: MercuryTransaction,
        historical: list[MercuryTransaction]
    ) -> Optional[Anomaly]:
        """Check if merchant is new/unusual"""

        merchant = transaction.counterparty_name or transaction.bank_description

        # Check if merchant appears in history
        seen_before = any(
            t.counterparty_name == merchant or merchant.lower() in t.bank_description.lower()
            for t in historical
        )

        if not seen_before and float(transaction.amount) > 100:
            # New merchant with significant amount
            return Anomaly(
                transaction=transaction,
                anomaly_type="unusual_merchant",
                severity="info" if float(transaction.amount) < 500 else "warning",
                reason=f"First transaction with {merchant}",
                expected_value="Known merchant",
                actual_value=merchant
            )

        return None

    def _check_unusual_timing(
        self,
        transaction: MercuryTransaction
    ) -> Optional[Anomaly]:
        """Check if transaction time is unusual"""

        hour = transaction.created_at.hour

        # Flag transactions outside business hours
        if hour < 6 or hour >= 22:
            return Anomaly(
                transaction=transaction,
                anomaly_type="unusual_timing",
                severity="info",
                reason=f"Transaction at {transaction.created_at.strftime('%I:%M %p')} (outside typical business hours)",
                expected_value="6am - 10pm",
                actual_value=transaction.created_at.strftime('%I:%M %p')
            )

        # Flag weekend transactions for certain types
        if transaction.created_at.weekday() >= 5:  # Saturday/Sunday
            if transaction.kind in ["outgoingDomesticWire", "outgoingAch"]:
                return Anomaly(
                    transaction=transaction,
                    anomaly_type="unusual_timing",
                    severity="info",
                    reason=f"Business payment on {transaction.created_at.strftime('%A')}",
                    expected_value="Weekday",
                    actual_value=transaction.created_at.strftime('%A')
                )

        return None

    def _check_duplicate(
        self,
        transaction: MercuryTransaction,
        historical: list[MercuryTransaction]
    ) -> Optional[Anomaly]:
        """Check for possible duplicate transaction"""

        # Look for transactions in past 48 hours with same amount and merchant
        recent = [
            t for t in historical
            if (transaction.created_at - t.created_at).days < 2
            and abs(float(t.amount) - float(transaction.amount)) < 0.01
            and (t.counterparty_name == transaction.counterparty_name
                 or t.bank_description == transaction.bank_description)
        ]

        if recent:
            return Anomaly(
                transaction=transaction,
                anomaly_type="duplicate_possible",
                severity="warning",
                reason=f"Similar transaction found within 48 hours: ${recent[0].amount} to same merchant",
                expected_value="No duplicate",
                actual_value=f"{len(recent)} similar transaction(s)"
            )

        return None

    def generate_alert_message(self, anomaly: Anomaly) -> str:
        """
        Generate human-readable alert message

        Args:
            anomaly: Detected anomaly

        Returns:
            Alert message string
        """

        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }

        emoji = severity_emoji.get(anomaly.severity, "⚠️")
        txn = anomaly.transaction

        message = f"{emoji} **{anomaly.anomaly_type.replace('_', ' ').title()}**\n\n"
        message += f"**Transaction:** ${txn.amount} to {txn.counterparty_name or txn.bank_description}\n"
        message += f"**Date:** {txn.created_at.strftime('%Y-%m-%d %I:%M %p')}\n"
        message += f"**Reason:** {anomaly.reason}\n\n"

        if anomaly.anomaly_type == "duplicate_possible":
            message += "Action: Review for duplicate payment\n"
        elif anomaly.anomaly_type == "unusual_amount":
            message += "Action: Verify this charge was expected\n"
        elif anomaly.anomaly_type == "unusual_merchant":
            message += "Action: Confirm this is a legitimate vendor\n"

        return message
