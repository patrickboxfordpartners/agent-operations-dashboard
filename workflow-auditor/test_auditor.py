#!/usr/bin/env python3
"""Test the workflow auditor with example input"""
import asyncio
import json
from shared.models import AuditInput, ClientInfo
from processing.auditor import auditor

# Example workflow description (you can replace this with real input)
EXAMPLE_WORKFLOW = """
We're a small accounting firm with 8 people. Our biggest pain point is client onboarding.

Here's how it works now:

1. Client fills out our intake form (takes them 20-30 minutes, lots of fields)
2. Office manager reviews it manually, checks for missing info (15 minutes per client)
3. If anything's missing, we email back and forth (can take 2-3 days)
4. Once complete, office manager manually enters into our CRM (10 minutes)
5. Then creates a folder structure in Google Drive (5 minutes)
6. Sends welcome email with next steps (5 minutes, but we forget sometimes)

We onboard 10-15 new clients per month. The whole process takes about 45 minutes of staff time per client, plus the back-and-forth delays. It's frustrating for clients and ties up our office manager.
"""

async def test_audit():
    """Run a test audit"""

    print("\n🧪 Testing Workflow Auditor\n")
    print("=" * 60)

    # Create test input
    audit_input = AuditInput(
        audit_id="test_001",
        client=ClientInfo(
            name="Test Accounting Firm",
            email="test@example.com",
            vertical="services",
            company_size="5-10",
            urgency="medium"
        ),
        input_type="text",
        content=EXAMPLE_WORKFLOW
    )

    # Generate audit
    try:
        audit_output = await auditor.generate_audit(audit_input)

        # Display results
        print("\n" + "=" * 60)
        print("📊 AUDIT RESULTS")
        print("=" * 60)

        print(f"\n**Workflow:** {audit_output.workflow.workflow_name}")
        print(f"**Steps:** {len(audit_output.workflow.steps)}")
        print(f"**Current Cost:** ${audit_output.workflow.current_cost.get('annual_cost', 0):,.0f}/year")

        print(f"\n**Solutions Generated:**")
        for key, solution in audit_output.solutions.items():
            if key.startswith('solution_'):
                savings = solution.estimated_outcomes.get('annual_savings', 0)
                payback = solution.build_cost.get('payback_months', 0)
                print(f"  • {solution.name}: ${savings:,.0f} savings, {payback:.1f}mo payback")

        print(f"\n**Recommended:** {audit_output.recommended_solution}")

        # Save to file
        output_file = "test_audit_output.json"
        with open(output_file, 'w') as f:
            json.dump(audit_output.model_dump(), f, indent=2, default=str)

        print(f"\n✅ Full audit saved to: {output_file}")
        print("\nNext: Create Notion database and output formatter")

    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audit())
