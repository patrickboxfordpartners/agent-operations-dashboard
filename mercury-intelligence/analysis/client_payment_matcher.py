"""Match incoming payments to clients/invoices"""
import json
from anthropic import Anthropic
from typing import Optional

from shared.models import MercuryTransaction, ClientPayment
from shared.config import config

class ClientPaymentMatcher:
    """Matches incoming transactions to clients"""

    def __init__(self, anthropic_api_key: str, known_clients: list[dict]):
        self.claude = Anthropic(api_key=anthropic_api_key)
        self.known_clients = known_clients  # [{"name": "...", "invoices": [...]}]

    async def check_payment(
        self,
        transaction: MercuryTransaction
    ) -> Optional[ClientPayment]:
        """
        Check if transaction is a client payment

        Args:
            transaction: Incoming transaction

        Returns:
            ClientPayment if matched, None otherwise
        """

        # Only check incoming transactions
        if transaction.kind not in ["incomingAch", "incomingDomesticWire", "incomingInternationalWire"]:
            return None

        # Skip small amounts (likely not invoices)
        if float(transaction.amount) < 100:
            return None

        # Use AI to match
        prompt = f"""Determine if this incoming payment is from a client.

TRANSACTION:
- Amount: ${transaction.amount}
- From: {transaction.counterparty_name or "Unknown"}
- Description: {transaction.bank_description}
- Note: {transaction.note or "None"}
- Date: {transaction.created_at.strftime('%Y-%m-%d')}

KNOWN CLIENTS:
{self._format_clients()}

Questions:
1. Is this payment likely from one of the known clients?
2. Which client (if any)?
3. Confidence (0-1)
4. Does it match an outstanding invoice?

Return JSON:
{{
  "is_client_payment": true,
  "client_name": "Client Name",
  "confidence": 0.92,
  "matched_invoice_id": "inv_123" or null,
  "reasoning": "Why this is/isn't a client payment"
}}

If NOT a client payment, return:
{{
  "is_client_payment": false,
  "client_name": null,
  "confidence": 0.0,
  "matched_invoice_id": null,
  "reasoning": "Explanation"
}}
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=800,
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

        if not data.get("is_client_payment"):
            return None

        # Build ClientPayment
        client_payment = ClientPayment(
            transaction=transaction,
            client_name=data["client_name"],
            confidence=data["confidence"],
            matched_invoice_id=data.get("matched_invoice_id")
        )

        # Calculate variance if invoice matched
        if client_payment.matched_invoice_id:
            invoice = self._find_invoice(client_payment.matched_invoice_id)
            if invoice:
                expected = invoice.get("amount")
                if expected:
                    client_payment.expected_amount = expected
                    client_payment.amount_variance = float(transaction.amount) - float(expected)

        return client_payment

    def _format_clients(self) -> str:
        """Format known clients for prompt"""

        if not self.known_clients:
            return "No known clients configured"

        lines = []
        for client in self.known_clients:
            line = f"- {client['name']}"
            if client.get('invoices'):
                outstanding = [inv for inv in client['invoices'] if inv.get('status') == 'unpaid']
                if outstanding:
                    amounts = ', '.join(f"${inv['amount']}" for inv in outstanding[:3])
                    line += f" (Outstanding invoices: {amounts})"
            lines.append(line)

        return "\n".join(lines)

    def _find_invoice(self, invoice_id: str) -> Optional[dict]:
        """Find invoice by ID"""
        for client in self.known_clients:
            for invoice in client.get('invoices', []):
                if invoice.get('id') == invoice_id:
                    return invoice
        return None

    def generate_notification(self, payment: ClientPayment) -> str:
        """
        Generate notification message for client payment

        Args:
            payment: Detected client payment

        Returns:
            Notification message
        """

        txn = payment.transaction

        message = f"💰 **Client Payment Received**\n\n"
        message += f"**Client:** {payment.client_name}\n"
        message += f"**Amount:** ${txn.amount}\n"
        message += f"**Date:** {txn.created_at.strftime('%Y-%m-%d')}\n"

        if payment.matched_invoice_id:
            message += f"**Invoice:** {payment.matched_invoice_id}\n"
            if payment.amount_variance:
                if abs(payment.amount_variance) < 1:
                    message += "✅ Amount matches invoice\n"
                else:
                    variance_str = f"${abs(payment.amount_variance):.2f} {'over' if payment.amount_variance > 0 else 'under'}"
                    message += f"⚠️ Amount variance: {variance_str}\n"
        else:
            message += "**Invoice:** Not matched - manual review needed\n"

        message += f"\n**Confidence:** {payment.confidence:.0%}\n"

        message += f"\n**Next steps:**\n"
        message += f"- [ ] Post to accounting\n"
        message += f"- [ ] Send thank you email\n"
        if payment.matched_invoice_id:
            message += f"- [ ] Mark invoice as paid\n"

        return message
