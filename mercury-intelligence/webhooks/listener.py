"""Mercury webhook listener"""
import hmac
import hashlib
from datetime import datetime
from typing import Optional

from shared.models import WebhookEvent, MercuryTransaction
from shared.config import config

class WebhookListener:
    """Listens for Mercury webhook events"""

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Mercury

        Args:
            payload: Raw request body
            signature: X-Mercury-Signature header

        Returns:
            True if valid
        """

        if not config.MERCURY_WEBHOOK_SECRET:
            # In dev mode, skip verification
            return True

        expected = hmac.new(
            config.MERCURY_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def handle_webhook(self, payload: dict) -> Optional[WebhookEvent]:
        """
        Process incoming webhook

        Args:
            payload: Webhook JSON payload

        Returns:
            WebhookEvent or None if invalid
        """

        event_type = payload.get("type")

        if event_type not in ["transaction.created", "transaction.updated"]:
            return None

        # Parse transaction
        txn_data = payload.get("transaction")
        if not txn_data:
            return None

        transaction = MercuryTransaction(
            id=txn_data["id"],
            status=txn_data["status"],
            amount=abs(float(txn_data["amount"])),  # Mercury uses negative for debits
            bank_description=txn_data.get("bankDescription", ""),
            counterparty_name=txn_data.get("counterpartyName"),
            counterparty_id=txn_data.get("counterpartyId"),
            created_at=datetime.fromisoformat(txn_data["createdAt"].replace("Z", "+00:00")),
            posted_at=datetime.fromisoformat(txn_data["postedAt"].replace("Z", "+00:00")) if txn_data.get("postedAt") else None,
            kind=txn_data.get("kind", "other"),
            note=txn_data.get("note"),
            has_receipt=txn_data.get("hasReceipt", False),
            account_id=txn_data["accountId"]
        )

        return WebhookEvent(
            event_type=event_type,
            transaction=transaction
        )

# For FastAPI integration
"""
from fastapi import FastAPI, Request, HTTPException
from webhooks.listener import WebhookListener

app = FastAPI()
listener = WebhookListener()

@app.post("/webhooks/mercury")
async def mercury_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Mercury-Signature", "")
    body = await request.body()

    if not listener.verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload = await request.json()
    event = await listener.handle_webhook(payload)

    if not event:
        raise HTTPException(status_code=400, detail="Invalid event")

    # Process event (categorize, detect patterns, etc)
    await process_event(event)

    return {"status": "ok"}
"""
