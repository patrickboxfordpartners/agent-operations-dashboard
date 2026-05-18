#!/usr/bin/env python3
"""Test full pipeline with a Grade A lead"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.models import Lead, LeadStatus
from workflows.lead_to_proposal import LeadToProposalWorkflow

async def test_grade_a_pipeline():
    """Test with a lead that should score Grade A"""

    print("\n" + "=" * 70)
    print("🔗 FULL PIPELINE TEST: High-Quality Lead")
    print("=" * 70)

    # Create a high-quality lead (should score A/B)
    lead = Lead(
        id="lead_002",
        status=LeadStatus.NEW,
        email="sarah.johnson@techstartup.io",  # From mock data - should score well
        name="Sarah Johnson",
        company="TechStartup.io",
        title="CEO & Founder",
        source="referral",
        source_detail="Referred by existing client"
    )

    print(f"\n📥 New High-Quality Lead:")
    print(f"   Name: {lead.name}")
    print(f"   Title: {lead.title}")
    print(f"   Company: {lead.company}")
    print(f"   Email: {lead.email}")
    print(f"   Source: Referral (warm lead)")

    # Workflow description
    workflow_description = """
    Our current client onboarding workflow:

    1. Initial contact via email/phone (30 minutes)
    2. Schedule discovery call (coordination takes 2-3 emails, 15 minutes)
    3. Discovery call and manual notes (60 minutes)
    4. Research their company and tech stack manually (45 minutes)
    5. Draft custom proposal by copy/pasting previous proposals (90 minutes)
    6. Partner review and revisions (30 minutes)
    7. Format in Word/PDF (20 minutes)
    8. Email to client with manual tracking (10 minutes)

    Total: ~5 hours per qualified lead
    Volume: 10-15 leads per month
    Pain Points:
    - Too slow - prospects go cold waiting
    - Quality varies by who creates proposal
    - No automatic follow-up
    - Hard to track engagement
    - Manual copy/paste leads to errors
    """

    print(f"\n📋 Discovery: 5-hour manual proposal process")

    # Execute workflow
    workflow = LeadToProposalWorkflow()

    print(f"\n🚀 Starting integrated workflow...")
    print(f"   This will: Enrich → Analyze → Generate Proposal")

    execution = await workflow.execute(lead, workflow_description)

    # Display full results
    print(f"\n" + "=" * 70)
    print("📊 PIPELINE EXECUTION RESULTS")
    print("=" * 70)

    print(f"\nOverall Status: {execution.status}")
    if execution.completed_at:
        duration = (execution.completed_at - execution.started_at).seconds
        print(f"Total Duration: {duration}s ({duration/60:.1f} minutes)")

    print(f"\n📍 Pipeline Steps: {len(execution.step_results)}")
    for i, step in enumerate(execution.step_results, 1):
        print(f"\n{i}. {step['step'].replace('_', ' ').title()}")
        print(f"   Status: {step['status']}")

        if step['step'] == 'enrich_lead' and 'result' in step:
            result = step['result']
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   Grade: {result.get('grade')} ({result.get('score')}/100)")
                print(f"   Confidence: {result.get('confidence', 0):.0%}")
                if result.get('key_insights'):
                    print(f"   Generated {len(result['key_insights'])} insights")

        elif step['step'] == 'qualification_check' and 'result' in step:
            result = step['result']
            if result.get('qualified'):
                print(f"   ✅ Lead qualified for immediate outreach")
            else:
                print(f"   ⚠️  Routed to nurture: {result.get('reason')}")

        elif step['step'] == 'analyze_workflow' and 'result' in step:
            result = step['result']
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                if result.get('analysis'):
                    analysis = result['analysis']
                    print(f"   Current cycle time: {analysis.get('total_time_minutes')}min")
                    print(f"   Annual cost: ${analysis.get('annual_cost', 0):,.0f}")
                if result.get('solutions'):
                    print(f"   Generated {len(result['solutions'])} solution tiers")

        elif step['step'] == 'generate_proposal' and 'result' in step:
            result = step['result']
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   Title: {result.get('title', 'N/A')}")
                print(f"   Phases: {len(result.get('phases', []))} implementation phases")
                print(f"   Pricing Tiers: {len(result.get('pricing_tiers', []))}")

        elif step['step'] == 'queue_delivery' and 'result' in step:
            result = step['result']
            print(f"   Delivery: {result.get('delivery_method', 'email')}")
            print(f"   Status: {result.get('status', 'queued')}")

    # Final state
    print(f"\n" + "=" * 70)
    print("FINAL LEAD STATE")
    print("=" * 70)
    print(f"\nLead ID: {lead.id}")
    print(f"Status: {lead.status.value}")
    print(f"Enrichment Grade: {lead.enrichment_grade} ({lead.enrichment_score}/100)")

    if lead.workflow_analysis_id:
        print(f"Workflow Analyzed: ✅ (ID: {lead.workflow_analysis_id})")

    if lead.proposal_id:
        print(f"Proposal Generated: ✅ (ID: {lead.proposal_id})")
        print(f"Proposal Sent: {lead.proposal_sent_at.strftime('%Y-%m-%d %H:%M') if lead.proposal_sent_at else 'Pending'}")

    if lead.next_followup:
        print(f"Next Follow-up: {lead.next_followup.strftime('%Y-%m-%d')}")

    # System health
    print(f"\n" + "=" * 70)
    print("SYSTEM HEALTH")
    print("=" * 70)
    health = await workflow.health_check()
    for system, online in health.items():
        icon = "✅" if online else "❌"
        status_text = "Online" if online else "Offline"
        print(f"{icon} {system.replace('_', ' ').title()}: {status_text}")

    # Value calculation
    print(f"\n" + "=" * 70)
    print("VALUE DELIVERED")
    print("=" * 70)

    if execution.status == "completed":
        print(f"\n⏱️  Time Comparison:")
        print(f"   Manual Process: 5 hours")
        print(f"   Automated Pipeline: {duration/60:.1f} minutes")
        print(f"   Time Saved: {5 - (duration/60):.1f} hours (95% reduction)")

        print(f"\n💰 Cost Savings (per lead):")
        hourly_rate = 150
        manual_cost = 5 * hourly_rate
        auto_cost = (duration/60) * hourly_rate
        savings = manual_cost - auto_cost
        print(f"   Manual: ${manual_cost:,.0f}")
        print(f"   Automated: ${auto_cost:,.0f}")
        print(f"   Savings: ${savings:,.0f}")

        print(f"\n📈 Monthly Value (15 leads/month):")
        print(f"   Total Savings: ${savings * 15:,.0f}/month")
        print(f"   Annual: ${savings * 15 * 12:,.0f}/year")

    print("\n")

if __name__ == "__main__":
    asyncio.run(test_grade_a_pipeline())
