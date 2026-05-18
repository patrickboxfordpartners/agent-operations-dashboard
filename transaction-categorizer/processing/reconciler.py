"""Reconciliation engine"""
from typing import Optional
from datetime import timedelta

from shared.models import (
    Transaction,
    CategorizedTransaction,
    ReconciliationResult
)

class Reconciler:
    """Reconciles transactions against accounting software"""

    def __init__(self, accounting_client):
        self.accounting = accounting_client

    async def reconcile_transaction(
        self,
        transaction: CategorizedTransaction
    ) -> ReconciliationResult:
        """
        Check if transaction already exists in accounting software

        Args:
            transaction: Categorized transaction to reconcile

        Returns:
            ReconciliationResult with match status
        """

        # Query accounting software for potential matches
        result = await self.accounting.reconcile(transaction)

        # If found potential matches, analyze them
        if result.status == "matched":
            return result

        # Check for near-duplicates (same day, similar amount)
        # This catches cases where descriptions differ slightly
        near_matches = await self._find_near_duplicates(transaction)

        if near_matches:
            result.status = "conflict"
            result.matches = near_matches
            result.conflict_reason = f"Found {len(near_matches)} similar transactions on same day"
            result.suggested_action = "Review manually - may be duplicate with different description"

        return result

    async def _find_near_duplicates(
        self,
        transaction: CategorizedTransaction
    ) -> list[dict]:
        """
        Find transactions that might be duplicates

        Same date, amount within 5%, description similarity
        """

        # In production, query accounting software with:
        # - Same date (or +/- 1 day for processing delays)
        # - Amount within 5%
        # - Calculate description similarity

        # For now, return empty
        return []

    async def batch_reconcile(
        self,
        transactions: list[CategorizedTransaction]
    ) -> list[ReconciliationResult]:
        """
        Reconcile multiple transactions

        Args:
            transactions: List of categorized transactions

        Returns:
            List of reconciliation results
        """

        results = []
        for txn in transactions:
            result = await self.reconcile_transaction(txn)
            results.append(result)

        return results

    def generate_reconciliation_report(
        self,
        results: list[ReconciliationResult]
    ) -> dict:
        """
        Generate summary report

        Args:
            results: List of reconciliation results

        Returns:
            Summary statistics
        """

        by_status = {
            "new": 0,
            "matched": 0,
            "duplicate": 0,
            "conflict": 0
        }

        for result in results:
            by_status[result.status] += 1

        return {
            "total": len(results),
            "by_status": by_status,
            "conflicts": [
                {
                    "transaction_id": r.transaction_id,
                    "reason": r.conflict_reason,
                    "suggested_action": r.suggested_action
                }
                for r in results
                if r.status == "conflict"
            ],
            "duplicates": [
                r.transaction_id
                for r in results
                if r.status == "duplicate"
            ],
            "ready_to_post": [
                r.transaction_id
                for r in results
                if r.status == "new"
            ]
        }
