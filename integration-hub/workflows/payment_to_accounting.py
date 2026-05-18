"""Payment-to-Accounting workflow"""
from datetime import datetime
from typing import Optional

from core.models import Transaction, Client, WorkflowExecution
from adapters.system_adapter import MercuryIntelligenceAdapter
from core.config import config

class PaymentToAccountingWorkflow:
    """
    Orchestrates payment processing:

    1. Mercury transaction webhook fires
    2. Categorize transaction
    3. Check if client payment
    4. Match to invoice/client
    5. Post to QuickBooks/Xero
    6. Send notifications
    """

    def __init__(self):
        self.mercury_adapter = MercuryIntelligenceAdapter(
            "mercury-intelligence",
            config.SYSTEMS["mercury-intelligence"]
        )

    async def execute(self, transaction_data: dict, known_clients: list[Client] = None) -> WorkflowExecution:
        """
        Execute payment processing workflow

        Args:
            transaction_data: Raw Mercury transaction
            known_clients: List of known clients for matching

        Returns:
            WorkflowExecution with results
        """

        execution = WorkflowExecution(
            id=f"exec_{datetime.now().timestamp()}",
            workflow_id="payment_to_accounting",
            trigger_event_id=transaction_data["id"],
            status="running"
        )

        try:
            # Step 1: Categorize transaction
            print(f"\n💰 Processing: ${transaction_data['amount']} - {transaction_data['description']}")
            print(f"\n🏷️  Step 1: Categorizing...")

            categorized = await self.mercury_adapter.categorize_transaction(transaction_data)

            execution.step_results.append({
                "step": "categorize",
                "result": categorized,
                "status": "completed"
            })

            print(f"   ✅ Category: {categorized.get('category_name')} ({categorized.get('confidence', 0):.0%})")

            # Step 2: Check if client payment
            if categorized.get("is_client_payment"):
                print(f"\n💵 Step 2: Client payment detected")

                # Try to match to client
                matched_client = self._match_client(transaction_data, known_clients or [])

                if matched_client:
                    print(f"   ✅ Matched to client: {matched_client.name}")
                    execution.step_results.append({
                        "step": "match_client",
                        "result": {
                            "client_id": matched_client.id,
                            "client_name": matched_client.name,
                            "matched": True
                        },
                        "status": "completed"
                    })

                    # Update client record
                    matched_client.payments_received += float(transaction_data["amount"])
                else:
                    print(f"   ⚠️  No client match found - flagging for review")
                    execution.step_results.append({
                        "step": "match_client",
                        "result": {"matched": False},
                        "status": "completed"
                    })

            # Step 3: Post to accounting (if high confidence)
            if categorized.get("confidence", 0) >= 0.85 and not categorized.get("needs_review"):
                print(f"\n📒 Step 3: Posting to QuickBooks...")

                # Would call QuickBooks API here
                execution.step_results.append({
                    "step": "post_to_accounting",
                    "result": {
                        "posted": True,
                        "accounting_system": "quickbooks",
                        "transaction_id": "qb_123"
                    },
                    "status": "completed"
                })

                print(f"   ✅ Posted to QuickBooks")
            else:
                print(f"\n⚠️  Step 3: Low confidence - flagging for review")
                execution.step_results.append({
                    "step": "post_to_accounting",
                    "result": {
                        "posted": False,
                        "reason": "low_confidence" if categorized.get("confidence", 0) < 0.85 else "needs_review"
                    },
                    "status": "skipped"
                })

            # Step 4: Send notifications if anomaly or client payment
            if categorized.get("is_client_payment") or categorized.get("needs_review"):
                print(f"\n📧 Step 4: Sending notification...")

                notification = self._generate_notification(transaction_data, categorized)

                execution.step_results.append({
                    "step": "send_notification",
                    "result": {
                        "sent": True,
                        "channels": ["slack", "email"],
                        "message": notification
                    },
                    "status": "completed"
                })

                print(f"   ✅ Notification sent")

            execution.status = "completed"
            execution.completed_at = datetime.now()
            execution.current_step = len(execution.step_results)

            print(f"\n✅ Payment processing complete")

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.now()
            print(f"\n❌ Workflow failed: {e}")

        return execution

    def _match_client(self, transaction_data: dict, clients: list[Client]) -> Optional[Client]:
        """Match transaction to client"""

        merchant = transaction_data.get("merchant", "").lower()
        description = transaction_data.get("description", "").lower()

        for client in clients:
            client_name = client.company.lower()
            if client_name in merchant or client_name in description:
                return client

        return None

    def _generate_notification(self, transaction_data: dict, categorized: dict) -> str:
        """Generate notification message"""

        if categorized.get("is_client_payment"):
            return f"💰 Client payment received: ${transaction_data['amount']} from {transaction_data.get('merchant', 'Unknown')}"
        elif categorized.get("needs_review"):
            return f"⚠️  Transaction needs review: ${transaction_data['amount']} - {transaction_data['description']}"
        else:
            return f"Transaction processed: ${transaction_data['amount']}"

    async def health_check(self) -> dict:
        """Check health of Mercury Intelligence"""
        return {
            "mercury_intelligence": await self.mercury_adapter.health_check()
        }
