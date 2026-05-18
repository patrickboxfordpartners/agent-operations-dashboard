#!/usr/bin/env python3
"""Test Integration Hub workflows"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add integration-hub to path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import Lead, LeadStatus, Client
from workflows.lead_to_proposal import LeadToProposalWorkflow
from workflows.payment_to_accounting import PaymentToAccountingWorkflow

async def test_lead_to_proposal_workflow():
    """Test the full Lead → Enrichment → Workflow → Proposal pipeline"""

    print("\n" + "=" * 70)
    print("🔗 TESTING: Lead-to-Proposal Workflow")
    print("=" * 70)

    # Create a test lead
    lead = Lead(
        id="lead_001",
        status=LeadStatus.NEW,
        email="jennifer@smithlaw.com",
        name="Jennifer Smith",
        company="Smith & Associates Law Firm",
        title="Managing Partner",
        source="linkedin",
        source_detail="Connected via mutual connection"
    )

    print(f"\n📥 New Lead: {lead.name} ({lead.company})")
    print(f"   Email: {lead.email}")
    print(f"   Source: {lead.source}")

    # Workflow description from discovery call
    workflow_description = """
    Our client intake process:

    1. Client fills out intake form (30 minutes)
    2. Office staff manually enters data into Clio (15 minutes)
    3. Partner reviews for conflicts (45 minutes manual searching)
    4. Generate engagement letter by copy/paste from template (60 minutes)

    Total: 2.5 hours per new client
    Volume: 15 new clients per month
    Pain: Manual, error-prone, consuming billable time
    """

    print(f"\n📋 Discovery Notes: Client intake workflow taking 2.5 hrs/client")

    # Execute workflow
    workflow = LeadToProposalWorkflow()

    print(f"\n🚀 Starting workflow...")
    execution = await workflow.execute(lead, workflow_description)

    # Display results
    print(f"\n" + "=" * 70)
    print("📊 WORKFLOW RESULTS")
    print("=" * 70)

    print(f"\nStatus: {execution.status}")
    print(f"Duration: {(execution.completed_at - execution.started_at).seconds}s" if execution.completed_at else "In progress")

    print(f"\nSteps Completed: {len(execution.step_results)}")
    for i, step in enumerate(execution.step_results, 1):
        print(f"\n{i}. {step['step'].replace('_', ' ').title()}: {step['status']}")
        if step['step'] == 'enrich_lead' and 'result' in step:
            result = step['result']
            print(f"   Score: {result.get('score')}/100 (Grade {result.get('grade')})")
            if result.get('key_insights'):
                print(f"   Insights: {len(result.get('key_insights'))} insights generated")

        elif step['step'] == 'analyze_workflow' and 'result' in step:
            result = step['result']
            if result.get('analysis'):
                analysis = result['analysis']
                print(f"   Current time: {analysis.get('total_time_minutes')} min/cycle")
                print(f"   Annual cost: ${analysis.get('annual_cost', 0):,.0f}")

        elif step['step'] == 'generate_proposal' and 'result' in step:
            result = step['result']
            print(f"   Proposal: {result.get('title', 'Generated')}")
            print(f"   Phases: {len(result.get('phases', []))} implementation phases")
            print(f"   Pricing: {len(result.get('pricing_tiers', []))} tiers")

    # Final lead state
    print(f"\n" + "=" * 70)
    print("FINAL LEAD STATE")
    print("=" * 70)
    print(f"\nStatus: {lead.status.value}")
    print(f"Grade: {lead.enrichment_grade} ({lead.enrichment_score}/100)")
    print(f"Proposal ID: {lead.proposal_id}")
    print(f"Ready for: Delivery via email")

    return execution


async def test_payment_to_accounting_workflow():
    """Test the Payment → Categorize → Match → Post pipeline"""

    print("\n\n" + "=" * 70)
    print("🔗 TESTING: Payment-to-Accounting Workflow")
    print("=" * 70)

    # Mock Mercury transaction (client payment)
    transaction = {
        "id": "txn_mercury_001",
        "status": "sent",
        "amount": 5000.00,
        "description": "ACH CREDIT FROM ACME CORP",
        "merchant": "ACME Corp",
        "date": datetime.now().isoformat(),
        "kind": "incomingAch",
        "account_id": "acc_123"
    }

    # Known clients
    clients = [
        Client(
            id="client_001",
            lead_id="lead_converted_001",
            email="contact@acmecorp.com",
            name="John Doe",
            company="ACME Corp",
            contract_value=15000.0,
            contract_signed_at=datetime.now(),
            payments_received=0.0,
            payments_pending=5000.0,
            invoices=["inv_2024_001"]
        )
    ]

    # Execute workflow
    workflow = PaymentToAccountingWorkflow()
    execution = await workflow.execute(transaction, clients)

    # Display results
    print(f"\n" + "=" * 70)
    print("📊 WORKFLOW RESULTS")
    print("=" * 70)

    print(f"\nStatus: {execution.status}")

    print(f"\nSteps Completed: {len(execution.step_results)}")
    for i, step in enumerate(execution.step_results, 1):
        print(f"{i}. {step['step'].replace('_', ' ').title()}: {step['status']}")

    return execution


async def test_health_checks():
    """Test system health checks"""

    print("\n\n" + "=" * 70)
    print("🏥 SYSTEM HEALTH CHECKS")
    print("=" * 70)

    lead_workflow = LeadToProposalWorkflow()
    payment_workflow = PaymentToAccountingWorkflow()

    print("\n📊 Lead-to-Proposal Systems:")
    health = await lead_workflow.health_check()
    for system, status in health.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {system.replace('_', ' ').title()}: {'Online' if status else 'Offline'}")

    print("\n💰 Payment-to-Accounting Systems:")
    health = await payment_workflow.health_check()
    for system, status in health.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {system.replace('_', ' ').title()}: {'Online' if status else 'Offline'}")


async def main():
    """Run all integration tests"""

    print("\n" + "=" * 70)
    print("🔗 INTEGRATION HUB - System Integration Tests")
    print("=" * 70)

    # Test 1: Lead to Proposal
    await test_lead_to_proposal_workflow()

    # Test 2: Payment to Accounting
    await test_payment_to_accounting_workflow()

    # Test 3: Health Checks
    await test_health_checks()

    print("\n\n" + "=" * 70)
    print("✅ ALL INTEGRATION TESTS COMPLETE")
    print("=" * 70)

    print("\n💡 Next steps:")
    print("   1. Set up persistent storage (SQLite/PostgreSQL)")
    print("   2. Build event bus for pub/sub between systems")
    print("   3. Add webhook endpoints for external triggers")
    print("   4. Create monitoring dashboard")
    print("   5. Set up notification channels (Slack, email)")
    print("   6. Build admin UI for workflow management")
    print("   7. Add workflow analytics and reporting")
    print("   8. Deploy Integration Hub as service\n")


if __name__ == "__main__":
    asyncio.run(main())
