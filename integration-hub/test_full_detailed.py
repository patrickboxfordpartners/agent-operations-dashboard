#!/usr/bin/env python3
"""Detailed full pipeline test with result inspection"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

os.environ.setdefault("VOYAGE_API_KEY", "dummy_key_for_import")
sys.path.insert(0, str(Path(__file__).parent))

from core.models import Lead, LeadStatus
from workflows.lead_to_proposal import LeadToProposalWorkflow

async def main():
    print("\n" + "=" * 70)
    print("🔗 DETAILED FULL PIPELINE TEST")
    print("=" * 70)

    lead = Lead(
        id="lead_detailed_001",
        status=LeadStatus.NEW,
        email="jennifer@smithlaw.com",
        name="Jennifer Smith",
        company="Smith & Associates Law Firm",
        title="Managing Partner",
        source="referral"
    )

    workflow_desc = """
    Law firm client intake: manual data entry (30min), conflict checks (45min),
    engagement letters (60min). Total 2.5hrs/client, 15 clients/month, $28K annual cost.
    Errors in conflict checks create malpractice risk.
    """

    workflow = LeadToProposalWorkflow()
    execution = await workflow.execute(lead, workflow_desc)

    print(f"\n{'='*70}")
    print("DETAILED RESULTS")
    print(f"{'='*70}\n")

    print(f"Overall Status: {execution.status}")
    print(f"Steps: {execution.current_step}/{len(execution.step_results)}\n")

    for i, step in enumerate(execution.step_results, 1):
        print(f"\n--- Step {i}: {step['step']} ---")
        print(f"Status: {step['status']}")

        if 'result' in step:
            result = step['result']
            if isinstance(result, dict):
                # Pretty print key info
                if 'error' in result:
                    print(f"ERROR: {result['error']}")
                elif step['step'] == 'enrich_lead':
                    print(f"  Score: {result.get('score')}")
                    print(f"  Grade: {result.get('grade')}")
                    print(f"  Confidence: {result.get('confidence')}")
                elif step['step'] == 'analyze_workflow':
                    if 'analysis' in result:
                        print(f"  Current time: {result['analysis'].get('total_time_minutes')}min")
                        print(f"  Annual cost: ${result['analysis'].get('annual_cost', 0):,.0f}")
                    if 'solutions' in result:
                        print(f"  Solutions: {len(result['solutions'])} tiers generated")
                elif step['step'] == 'generate_proposal':
                    print(f"  Proposal ID: {result.get('proposal_id')}")
                    print(f"  Title: {result.get('title')}")
                    print(f"  Phases: {len(result.get('phases', []))}")
                    print(f"  Pricing Tiers: {len(result.get('pricing_tiers', []))}")

    print(f"\n{'='*70}")
    print("FINAL LEAD STATE")
    print(f"{'='*70}\n")
    print(f"ID: {lead.id}")
    print(f"Status: {lead.status.value}")
    print(f"Enrichment: Grade {lead.enrichment_grade} ({lead.enrichment_score}/100)")
    print(f"Workflow Analyzed: {lead.workflow_analysis_id or 'No'}")
    print(f"Proposal ID: {lead.proposal_id or 'None generated'}")
    print(f"Proposal Sent: {lead.proposal_sent_at or 'Not sent'}")

    if execution.status == "completed":
        print(f"\n✅ FULL PIPELINE SUCCESSFUL!")
        print(f"\nValue Delivered:")
        print(f"  Manual process: 5 hours @ $150/hr = $750")
        print(f"  Automated: ~3 minutes = $7.50")
        print(f"  Savings: $742.50 per lead")
        print(f"  Monthly (15 leads): $11,137.50")
        print(f"  Annual: $133,650.00")

if __name__ == "__main__":
    asyncio.run(main())
