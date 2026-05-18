"""Real-time transaction categorization"""
import json
import sys
from pathlib import Path

# Add parent for integration with Transaction Categorizer
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "transaction-categorizer"))

from anthropic import Anthropic
from shared.models import MercuryTransaction, CategorizedTransaction
from shared.config import config

class MercuryCategorizer:
    """Categorizes Mercury transactions in real-time"""

    def __init__(self, anthropic_api_key: str, categories: list[dict]):
        self.claude = Anthropic(api_key=anthropic_api_key)
        self.categories = categories

    async def categorize(
        self,
        transaction: MercuryTransaction,
        business_context: str = ""
    ) -> CategorizedTransaction:
        """
        Categorize a single Mercury transaction

        Args:
            transaction: Mercury transaction
            business_context: Optional business context

        Returns:
            CategorizedTransaction
        """

        # Build prompt
        prompt = f"""Categorize this business transaction.

TRANSACTION:
- Amount: ${transaction.amount}
- Description: {transaction.bank_description}
- Merchant: {transaction.counterparty_name or "Unknown"}
- Type: {transaction.kind}
- Note: {transaction.note or "None"}
- Date: {transaction.created_at.strftime('%Y-%m-%d')}

BUSINESS CONTEXT:
{business_context or "Technology consulting / AI automation business"}

AVAILABLE CATEGORIES:
{self._format_categories()}

Analyze this transaction and determine:

1. **Category** - Best fit from the list above
2. **Confidence** (0-1) - How certain are you?
3. **Reasoning** - Brief explanation
4. **Flags**:
   - needs_review: Should a human review this?
   - is_recurring: Is this likely a recurring charge?
   - is_client_payment: Is this a client paying an invoice?

IMPORTANT CONTEXT CLUES:
- ACH/Wire IN = likely client payment or refund
- ACH/Wire OUT = likely vendor payment
- Debit card = likely expense or subscription
- "Fee" kind = bank/processing fee
- Counterparty name often contains company name

Return JSON:
{{
  "category_id": "cat_002",
  "category_name": "Software & Subscriptions",
  "confidence": 0.92,
  "reasoning": "Dropbox is clearly a software subscription",
  "needs_review": false,
  "is_recurring": true,
  "is_client_payment": false,
  "matched_client": null
}}
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse
        text = response.content[0].text
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        data = json.loads(text)

        return CategorizedTransaction(
            transaction=transaction,
            category_id=data["category_id"],
            category_name=data["category_name"],
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            needs_review=data.get("needs_review", False),
            is_recurring=data.get("is_recurring", False),
            is_client_payment=data.get("is_client_payment", False),
            matched_client=data.get("matched_client")
        )

    def _format_categories(self) -> str:
        """Format categories for prompt"""
        if not self.categories:
            # Default categories for consulting business
            return """
- cat_001: Client Revenue (income from clients)
- cat_002: Software & Subscriptions (SaaS tools)
- cat_003: Contractor Payments (1099 contractors)
- cat_004: Professional Services (lawyers, accountants)
- cat_005: Marketing & Advertising
- cat_006: Office & Supplies
- cat_007: Travel & Meals
- cat_008: Bank Fees
- cat_009: Taxes & Licenses
- cat_010: Owner Draw
- cat_011: Uncategorized
"""

        lines = []
        for cat in self.categories:
            line = f"- {cat['id']}: {cat['name']}"
            if cat.get('keywords'):
                line += f" ({', '.join(cat['keywords'])})"
            lines.append(line)
        return "\n".join(lines)
