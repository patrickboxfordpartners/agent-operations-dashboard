#!/usr/bin/env python3
"""Force full pipeline execution regardless of health checks"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Set Voyage API key to prevent import errors (even if dummy)
os.environ.setdefault("VOYAGE_API_KEY", "dummy_key_for_import")

sys.path.insert(0, str(Path(__file__).parent))

from core.models import Lead, LeadStatus
from workflows.lead_to_proposal import LeadToProposalWorkflow

async def test_forced_pipeline():
    """Force execution of full pipeline"""

    print("\n" + "=" * 70)
    print("🔗 FORCED FULL PIPELINE TEST")
    print("=" * 70)

    # Use Jennifer Smith from law firm (better match for our ICP)
    lead = Lead(
        id="lead_law_001",
        status=LeadStatus.NEW,
        email="jennifer@smithlaw.com",
        name="Jennifer Smith",
        company="Smith & Associates Law Firm",
        title="Managing Partner",
        source="referral",
        source_detail="Referred by ACME Corp"
    )

    print(f"\n📥 Lead: {lead.name} - {lead.title}")
    print(f"   Company: {lead.company}")
    print(f"   Source: Warm referral")

    workflow_description = """
    Current client intake workflow at our law firm:

    Step 1: Client submits intake form online (30 minutes client time)
    - Often incomplete, requires follow-up
    - Data not structured

    Step 2: Office staff manually reviews and enters into Clio (15 minutes)
    - Prone to typos
    - Sometimes fields are skipped

    Step 3: Partner performs conflict check (45 minutes)
    - Manual search through client database
    - Check opposing parties, related entities
    - High risk if missed

    Step 4: Generate engagement letter (60 minutes)
    - Copy previous template
    - Find/replace client details
    - Version control issues
    - Formatting problems

    Total time: 2.5 hours per new client
    Frequency: 15 new clients per month
    Annual cost: $28,000 in staff time

    Pain points:
    - Error-prone manual data entry
    - Conflict check risk (malpractice exposure)
    - Slow turnaround (clients waiting 2-3 days)
    - Inconsistent engagement letters
    - No audit trail
    """

    print(f"\n📋 Workflow: Law firm client intake (2.5 hrs/client, $28K annual cost)")

    # Execute workflow
    print(f"\n🚀 Executing full pipeline...")
    print(f"   Step 1: Lead Enrichment...")

    workflow = LeadToProposalWorkflow()

    try:
        execution = await workflow.execute(lead, workflow_description)

        print(f"\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        print(f"\nStatus: {execution.status}")
        if execution.error:
            print(f"Error: {execution.error}")

        print(f"\nSteps completed: {len(execution.step_results)}")
        for step in execution.step_results:
            print(f"  ✓ {step['step']}: {step['status']}")

        print(f"\nFinal Lead State:")
        print(f"  Status: {lead.status.value}")
        print(f"  Grade: {lead.enrichment_grade} ({lead.enrichment_score}/100)")
        if lead.proposal_id:
            print(f"  Proposal ID: {lead.proposal_id}")
            print(f"  ✅ FULL PIPELINE COMPLETED")
        else:
            print(f"  ⚠️  Did not reach proposal generation")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_forced_pipeline())
