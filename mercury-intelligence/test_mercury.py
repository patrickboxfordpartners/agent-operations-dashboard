#!/usr/bin/env python3
"""Test Mercury Intelligence"""
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from decimal import Decimal

from shared.models import MercuryTransaction
from processing.categorizer import MercuryCategorizer
from analysis.recurring_detector import RecurringDetector
from analysis.anomaly_detector import AnomalyDetector
from analysis.client_payment_matcher import ClientPaymentMatcher

load_dotenv()

# Mock Mercury transactions
MOCK_TRANSACTIONS = [
    # Client payments
    MercuryTransaction(
        id="txn_001",
        status="sent",
        amount=Decimal("5000.00"),
        bank_description="ACH CREDIT FROM ACME CORP",
        counterparty_name="ACME Corp",
        created_at=datetime.now() - timedelta(days=1),
        posted_at=datetime.now() - timedelta(days=1),
        kind="incomingAch",
        note="Invoice #2024-001",
        has_receipt=False,
        account_id="acc_123"
    ),

    # Recurring subscription (Anthropic)
    MercuryTransaction(
        id="txn_002",
        status="sent",
        amount=Decimal("200.00"),
        bank_description="ANTHROPIC*CLAUDE",
        counterparty_name="Anthropic",
        created_at=datetime.now() - timedelta(days=2),
        posted_at=datetime.now() - timedelta(days=2),
        kind="debitCardTransaction",
        note=None,
        has_receipt=False,
        account_id="acc_123"
    ),

    # Normal expense
    MercuryTransaction(
        id="txn_003",
        status="sent",
        amount=Decimal("45.00"),
        bank_description="FIGMA INC",
        counterparty_name="Figma",
        created_at=datetime.now() - timedelta(days=3),
        posted_at=datetime.now() - timedelta(days=3),
        kind="debitCardTransaction",
        note=None,
        has_receipt=False,
        account_id="acc_123"
    ),

    # Anomaly - large unusual charge
    MercuryTransaction(
        id="txn_004",
        status="sent",
        amount=Decimal("3500.00"),
        bank_description="UNKNOWN VENDOR LLC",
        counterparty_name="Unknown Vendor",
        created_at=datetime.now() - timedelta(hours=2),
        posted_at=None,
        kind="outgoingAch",
        note=None,
        has_receipt=False,
        account_id="acc_123"
    ),

    # Weekend transaction (timing anomaly)
    MercuryTransaction(
        id="txn_005",
        status="sent",
        amount=Decimal("1200.00"),
        bank_description="WIRE TO CONTRACTOR",
        counterparty_name="John Smith",
        created_at=datetime.now().replace(hour=23, minute=30) - timedelta(days=6),
        posted_at=datetime.now() - timedelta(days=6),
        kind="outgoingDomesticWire",
        note="Contractor payment",
        has_receipt=False,
        account_id="acc_123"
    ),

    # Another client payment
    MercuryTransaction(
        id="txn_006",
        status="sent",
        amount=Decimal("12500.00"),
        bank_description="WIRE FROM TECHSTARTUP INC",
        counterparty_name="TechStartup Inc",
        created_at=datetime.now() - timedelta(days=4),
        posted_at=datetime.now() - timedelta(days=4),
        kind="incomingDomesticWire",
        note="Project milestone payment",
        has_receipt=False,
        account_id="acc_123"
    ),

    # Recurring - previous Anthropic charge
    MercuryTransaction(
        id="txn_007",
        status="sent",
        amount=Decimal("200.00"),
        bank_description="ANTHROPIC*CLAUDE",
        counterparty_name="Anthropic",
        created_at=datetime.now() - timedelta(days=32),
        posted_at=datetime.now() - timedelta(days=32),
        kind="debitCardTransaction",
        note=None,
        has_receipt=False,
        account_id="acc_123"
    ),

    # Recurring - even earlier Anthropic
    MercuryTransaction(
        id="txn_008",
        status="sent",
        amount=Decimal("200.00"),
        bank_description="ANTHROPIC*CLAUDE",
        counterparty_name="Anthropic",
        created_at=datetime.now() - timedelta(days=62),
        posted_at=datetime.now() - timedelta(days=62),
        kind="debitCardTransaction",
        note=None,
        has_receipt=False,
        account_id="acc_123"
    ),
]

# Known clients for payment matching
KNOWN_CLIENTS = [
    {
        "name": "ACME Corp",
        "invoices": [
            {"id": "inv_2024_001", "amount": 5000.00, "status": "unpaid"},
            {"id": "inv_2024_002", "amount": 3500.00, "status": "unpaid"}
        ]
    },
    {
        "name": "TechStartup Inc",
        "invoices": [
            {"id": "inv_2024_003", "amount": 12500.00, "status": "unpaid"}
        ]
    }
]

async def test_mercury_intelligence():
    """Test full Mercury Intelligence pipeline"""

    print("\n💰 Testing Mercury Intelligence\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    # Initialize components
    categorizer = MercuryCategorizer(api_key, categories=[])
    recurring_detector = RecurringDetector()
    anomaly_detector = AnomalyDetector()
    payment_matcher = ClientPaymentMatcher(api_key, KNOWN_CLIENTS)

    print(f"\n📊 Analyzing {len(MOCK_TRANSACTIONS)} transactions...\n")

    categorized = []
    recurring_found = []
    anomalies_found = []
    client_payments = []

    for i, txn in enumerate(MOCK_TRANSACTIONS, 1):
        print(f"\n{i}. Processing: ${txn.amount} - {txn.bank_description}")
        print(f"   Type: {txn.kind} | Date: {txn.created_at.strftime('%Y-%m-%d %H:%M')}")

        # 1. Categorize
        print(f"   🏷️  Categorizing...")
        cat_txn = await categorizer.categorize(txn, business_context="AI consulting business")
        categorized.append(cat_txn)
        print(f"   ✅ Category: {cat_txn.category_name} (confidence: {cat_txn.confidence:.0%})")
        print(f"   📝 Reasoning: {cat_txn.reasoning}")

        # 2. Check for recurring pattern
        if cat_txn.is_recurring:
            print(f"   🔁 Checking recurring pattern...")
            historical = [t for t in MOCK_TRANSACTIONS if t.id != txn.id]
            recurring = await recurring_detector.analyze_transaction(txn, historical)
            if recurring:
                recurring_found.append(recurring)
                print(f"   🔄 RECURRING: {recurring.frequency} charge, ~${recurring.avg_amount}/occurrence")
                print(f"      Annual cost: ${recurring.annual_cost}")

        # 3. Check for anomalies
        print(f"   🔍 Checking for anomalies...")
        historical = [t for t in MOCK_TRANSACTIONS if t.id != txn.id and t.created_at < txn.created_at]
        anomaly = await anomaly_detector.check_transaction(txn, historical)
        if anomaly:
            anomalies_found.append(anomaly)
            print(f"   ⚠️  ANOMALY: {anomaly.anomaly_type} ({anomaly.severity})")
            print(f"      {anomaly.reason}")

        # 4. Check if client payment
        if cat_txn.is_client_payment:
            print(f"   💰 Checking client payment match...")
            payment = await payment_matcher.check_payment(txn)
            if payment:
                client_payments.append(payment)
                print(f"   ✅ CLIENT PAYMENT: {payment.client_name} (confidence: {payment.confidence:.0%})")
                if payment.matched_invoice_id:
                    print(f"      Matched invoice: {payment.matched_invoice_id}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    print(f"\n✅ Categorized: {len(categorized)} transactions")
    print(f"   High confidence (>85%): {sum(1 for c in categorized if c.confidence >= 0.85)}")
    print(f"   Needs review: {sum(1 for c in categorized if c.needs_review)}")

    if recurring_found:
        print(f"\n🔄 Recurring Charges: {len(recurring_found)}")
        for rec in recurring_found:
            print(f"   - {rec.merchant}: ${rec.avg_amount} {rec.frequency} (${rec.annual_cost}/year)")

        insights = recurring_detector.generate_insights(recurring_found)
        print(f"\n💡 Recurring Insights:")
        for insight in insights:
            print(f"   {insight}")

    if anomalies_found:
        print(f"\n⚠️  Anomalies Detected: {len(anomalies_found)}")
        for anomaly in anomalies_found:
            print(f"\n   {anomaly.anomaly_type} ({anomaly.severity}):")
            print(f"   ${anomaly.transaction.amount} - {anomaly.transaction.bank_description}")
            print(f"   {anomaly.reason}")

    if client_payments:
        print(f"\n💰 Client Payments: {len(client_payments)}")
        for payment in client_payments:
            print(f"\n   {payment.client_name}: ${payment.transaction.amount}")
            if payment.matched_invoice_id:
                print(f"   Invoice: {payment.matched_invoice_id} ✅")
                if payment.amount_variance and abs(payment.amount_variance) > 0.01:
                    print(f"   Variance: ${payment.amount_variance:+.2f}")
            print(f"   Confidence: {payment.confidence:.0%}")

    print("\n" + "=" * 70)
    print("\n✅ Mercury Intelligence test complete!\n")
    print("💡 Next steps:")
    print("   1. Set up Mercury API credentials")
    print("   2. Configure webhook endpoint (FastAPI)")
    print("   3. Connect to QuickBooks/Xero for auto-posting")
    print("   4. Set up Slack notifications for anomalies")
    print("   5. Build dashboard for recurring charge monitoring")
    print("   6. Add email alerts for client payments")
    print("   7. Create monthly spend analysis report")
    print("   8. Integrate with Transaction Categorizer system\n")

if __name__ == "__main__":
    asyncio.run(test_mercury_intelligence())
