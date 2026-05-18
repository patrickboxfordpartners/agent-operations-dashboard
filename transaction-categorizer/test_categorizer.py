#!/usr/bin/env python3
"""Test transaction categorizer"""
import asyncio
import json
import os
from dotenv import load_dotenv
from datetime import datetime

from integration.plaid_client import get_mock_transactions
from integration.accounting_client import get_mock_categories, QuickBooksClient
from processing.categorizer import TransactionCategorizer
from processing.reconciler import Reconciler
from shared.models import CategorizationStats

load_dotenv()

async def test_categorizer():
    """Test full categorization pipeline"""

    print("\n💰 Testing Transaction Categorizer\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    # 1. Get mock transactions (Plaid)
    print("\n📊 Fetching transactions from Plaid...")
    transactions = get_mock_transactions()
    print(f"   ✅ Retrieved {len(transactions)} transactions")

    # 2. Get chart of accounts (QuickBooks/Xero)
    print("\n📁 Fetching chart of accounts...")
    categories = get_mock_categories()
    print(f"   ✅ Retrieved {len(categories)} categories")

    # Display transactions
    print("\n" + "=" * 70)
    print("TRANSACTIONS TO CATEGORIZE:")
    print("=" * 70)
    for txn in transactions:
        print(f"\n{txn.date.strftime('%Y-%m-%d')} | ${txn.amount:>10} | {txn.description}")
        print(f"   Merchant: {txn.merchant_name or 'Unknown'}")
        print(f"   Plaid Category: {' > '.join(txn.category_plaid) if txn.category_plaid else 'None'}")

    # 3. Categorize with Claude
    print("\n" + "=" * 70)
    print("🧠 CATEGORIZING WITH CLAUDE...")
    print("=" * 70)

    categorizer = TransactionCategorizer(api_key)

    business_context = """
Small consulting business (sole proprietor)
Main expenses: software tools, office supplies, travel, client meetings
Looking to categorize transactions for quarterly tax filing
"""

    start_time = datetime.now()

    categorized = await categorizer.categorize_batch(
        transactions=transactions,
        categories=categories,
        business_context=business_context
    )

    duration = (datetime.now() - start_time).total_seconds()

    # Display results
    print("\n✅ CATEGORIZATION COMPLETE\n")

    high_confidence = 0
    needs_review = 0

    for cat_txn in categorized:
        txn = cat_txn.transaction
        confidence_icon = "✅" if cat_txn.confidence >= 0.85 else "⚠️" if cat_txn.confidence >= 0.60 else "❌"
        review_icon = "🔍" if cat_txn.needs_review else "  "

        print(f"\n{review_icon} {txn.date.strftime('%Y-%m-%d')} | ${txn.amount:>10}")
        print(f"   Description: {txn.description}")
        print(f"   {confidence_icon} Category: {cat_txn.category_name} (confidence: {cat_txn.confidence:.0%})")
        print(f"   Reasoning: {cat_txn.reasoning}")

        if cat_txn.needs_review:
            print(f"   ⚠️  NEEDS REVIEW: {cat_txn.review_reason}")
            needs_review += 1

        if cat_txn.confidence >= 0.85:
            high_confidence += 1

    # 4. Reconciliation
    print("\n" + "=" * 70)
    print("🔄 RECONCILING WITH QUICKBOOKS...")
    print("=" * 70)

    accounting_client = QuickBooksClient()
    reconciler = Reconciler(accounting_client)

    reconciliation_results = await reconciler.batch_reconcile(categorized)
    reconciliation_report = reconciler.generate_reconciliation_report(reconciliation_results)

    print("\n✅ Reconciliation complete:")
    print(f"   New transactions: {reconciliation_report['by_status']['new']}")
    print(f"   Already matched: {reconciliation_report['by_status']['matched']}")
    print(f"   Duplicates found: {reconciliation_report['by_status']['duplicate']}")
    print(f"   Conflicts: {reconciliation_report['by_status']['conflict']}")

    if reconciliation_report['ready_to_post']:
        print(f"\n   📤 Ready to post: {len(reconciliation_report['ready_to_post'])} transactions")

    # 5. Statistics
    print("\n" + "=" * 70)
    print("📊 STATISTICS")
    print("=" * 70)

    stats = CategorizationStats(
        total_transactions=len(transactions),
        categorized=len(categorized),
        needs_review=needs_review,
        high_confidence=high_confidence,
        duplicates_found=reconciliation_report['by_status']['duplicate'],
        conflicts_found=reconciliation_report['by_status']['conflict'],
        cost_usd=0.10,  # Approximate
        duration_seconds=duration,
        categories_used={
            cat_txn.category_name: sum(
                1 for c in categorized if c.category_name == cat_txn.category_name
            )
            for cat_txn in categorized
        }
    )

    print(f"\nTotal Transactions: {stats.total_transactions}")
    print(f"Categorized: {stats.categorized}")
    print(f"High Confidence (>85%): {stats.high_confidence} ({stats.high_confidence/stats.total_transactions:.0%})")
    print(f"Needs Review: {stats.needs_review}")
    print(f"Duplicates: {stats.duplicates_found}")
    print(f"Conflicts: {stats.conflicts_found}")
    print(f"\nDuration: {stats.duration_seconds:.2f}s")
    print(f"Cost: ${stats.cost_usd:.2f}")

    print("\n📊 Category Distribution:")
    for category, count in sorted(stats.categories_used.items(), key=lambda x: -x[1]):
        print(f"   {category}: {count}")

    # 6. Save results
    print("\n" + "=" * 70)

    output_file = "categorized_transactions.json"
    with open(output_file, 'w') as f:
        json.dump(
            {
                "transactions": [
                    {
                        "transaction": {
                            "id": ct.transaction.id,
                            "date": ct.transaction.date.isoformat(),
                            "amount": str(ct.transaction.amount),
                            "description": ct.transaction.description,
                            "merchant": ct.transaction.merchant_name
                        },
                        "category": {
                            "id": ct.category_id,
                            "name": ct.category_name
                        },
                        "confidence": ct.confidence,
                        "reasoning": ct.reasoning,
                        "needs_review": ct.needs_review,
                        "review_reason": ct.review_reason
                    }
                    for ct in categorized
                ],
                "stats": {
                    "total": stats.total_transactions,
                    "high_confidence": stats.high_confidence,
                    "needs_review": stats.needs_review,
                    "categories_used": stats.categories_used
                },
                "reconciliation": reconciliation_report
            },
            f,
            indent=2
        )

    print(f"\n💾 Saved results to: {output_file}")

    print("\n✅ Transaction categorization complete!\n")
    print("💡 Next steps:")
    print("   1. Review flagged transactions")
    print("   2. Connect real Plaid account (get access token)")
    print("   3. Set up QuickBooks/Xero OAuth")
    print("   4. Create approval workflow for low-confidence txns")
    print("   5. Schedule daily runs (cron)")
    print("   6. Feed learnings back into Second Brain")
    print("   7. Add ML model for pattern recognition over time\n")

if __name__ == "__main__":
    asyncio.run(test_categorizer())
