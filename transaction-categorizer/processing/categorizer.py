"""AI-powered transaction categorization"""
import json
from anthropic import Anthropic

from shared.models import Transaction, Category, CategorizedTransaction
from shared.config import config

class TransactionCategorizer:
    """Categorizes transactions using Claude with business context"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def categorize_batch(
        self,
        transactions: list[Transaction],
        categories: list[Category],
        business_context: str = ""
    ) -> list[CategorizedTransaction]:
        """
        Categorize multiple transactions at once

        Args:
            transactions: List of transactions to categorize
            categories: Available categories from chart of accounts
            business_context: Optional context about the business

        Returns:
            List of categorized transactions
        """

        # Build category reference
        category_guide = self._build_category_guide(categories)

        # Build prompt with all transactions
        prompt = f"""You are an expert bookkeeper categorizing business transactions.

BUSINESS CONTEXT:
{business_context or "Small business / sole proprietor"}

AVAILABLE CATEGORIES:
{category_guide}

TRANSACTIONS TO CATEGORIZE:
{self._format_transactions(transactions)}

For each transaction, determine:
1. The best category from the list above
2. Your confidence (0-1)
3. Brief reasoning
4. Whether it needs manual review

RULES:
- Match merchant patterns and keywords when possible
- Consider typical business expenses for this type of business
- Flag unusual amounts or unclear merchants for review
- Use Plaid's category as a hint, but you decide the final category
- If unsure between categories, choose the more specific one
- Personal expenses should be flagged as "needs_review"

Return JSON array:
[
  {{
    "transaction_id": "txn_001",
    "category_id": "cat_002",
    "category_name": "Software & Subscriptions",
    "confidence": 0.95,
    "reasoning": "Dropbox is clearly software subscription",
    "needs_review": false,
    "review_reason": null
  }},
  ...
]
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        text = response.content[0].text
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        results = json.loads(text)

        # Build categorized transactions
        categorized = []
        txn_map = {t.id: t for t in transactions}

        for result in results:
            txn = txn_map[result["transaction_id"]]
            categorized.append(
                CategorizedTransaction(
                    transaction=txn,
                    category_id=result["category_id"],
                    category_name=result["category_name"],
                    confidence=result["confidence"],
                    reasoning=result["reasoning"],
                    needs_review=result["needs_review"],
                    review_reason=result.get("review_reason")
                )
            )

        return categorized

    def _build_category_guide(self, categories: list[Category]) -> str:
        """Format categories for prompt"""
        lines = []
        for cat in categories:
            line = f"- {cat.id}: {cat.name} ({cat.account_type})"
            if cat.keywords:
                line += f"\n  Keywords: {', '.join(cat.keywords)}"
            if cat.merchant_patterns:
                line += f"\n  Merchants: {', '.join(cat.merchant_patterns)}"
            lines.append(line)
        return "\n".join(lines)

    def _format_transactions(self, transactions: list[Transaction]) -> str:
        """Format transactions for prompt"""
        lines = []
        for txn in transactions:
            line = f"""
ID: {txn.id}
Date: {txn.date.strftime('%Y-%m-%d')}
Amount: ${txn.amount}
Description: {txn.description}
Merchant: {txn.merchant_name or 'Unknown'}
Account: {txn.account_type}
Plaid Category: {' > '.join(txn.category_plaid) if txn.category_plaid else 'None'}
---"""
            lines.append(line)
        return "\n".join(lines)

    async def learn_from_correction(
        self,
        transaction: Transaction,
        wrong_category: str,
        correct_category: str,
        user_note: str
    ) -> dict:
        """
        Learn from user corrections to improve future categorizations

        This would update category rules or store corrections
        for future reference.

        Args:
            transaction: The transaction that was miscategorized
            wrong_category: What we suggested
            correct_category: What user selected
            user_note: User's explanation

        Returns:
            Learning record
        """

        # In production, this would:
        # 1. Store the correction in a database
        # 2. Update category keywords/patterns
        # 3. Feed into Second Brain as a case study
        # 4. Influence future categorization prompts

        return {
            "transaction_id": transaction.id,
            "merchant": transaction.merchant_name,
            "description": transaction.description,
            "wrong_category": wrong_category,
            "correct_category": correct_category,
            "user_note": user_note,
            "learned_at": transaction.date.isoformat()
        }
