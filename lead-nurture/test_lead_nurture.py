#!/usr/bin/env python3
"""Test the lead nurture system"""
import asyncio
import json
import os
from dotenv import load_dotenv

from shared.models import Lead
from scoring.lead_scorer import LeadScorer
from sequences.email_generator import EmailSequenceGenerator

load_dotenv()

# Test leads with different characteristics
TEST_LEADS = [
    Lead(
        lead_id="lead_001_hot",
        name="Sarah Johnson",
        email="sarah@abcdental.com",
        company="ABC Dental Practice",
        vertical="healthcare",
        company_size="8 employees",
        source="website_form",
        message="""
        Hi, I'm the office manager at ABC Dental. We're spending 15+ hours per week
        on manual appointment scheduling and it's costing us about $15k annually in
        staff time. I saw your case study with SmileCare Dental and we have the exact
        same pain points. We have budget approved to fix this ASAP - our busy season
        starts in 6 weeks. Can we schedule a call this week?
        """
    ),
    Lead(
        lead_id="lead_002_medium",
        name="Tom Martinez",
        email="tom@lawfirm.com",
        company="Martinez & Associates Law",
        vertical="legal",
        company_size="5-10",
        source="linkedin_dm",
        message="""
        Hey, came across your profile and saw you do AI automation for small businesses.
        We're a small law firm and client intake is taking forever. Not sure exactly
        what we need but curious to learn more about what's possible. What do you
        typically charge for something like this?
        """
    ),
    Lead(
        lead_id="lead_003_low",
        name="Alex Chen",
        email="alex@startup.com",
        company="TechStartup Inc",
        vertical="saas",
        company_size="unknown",
        source="email",
        message="""
        Hi, I'm exploring AI tools for our business. Just seeing what's out there.
        Can you send me some information about your services?
        """
    )
]

async def test_nurture_system():
    """Test the full lead nurture pipeline"""

    print("\n🎯 Testing Lead Nurture System\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    scorer = LeadScorer(api_key)
    email_gen = EmailSequenceGenerator(api_key)

    results = []

    for lead in TEST_LEADS:
        print(f"\n📧 Processing: {lead.name} from {lead.company}")
        print(f"   Source: {lead.source}")
        print(f"   Message preview: {lead.message[:80]}...")

        # Score the lead
        print("   🔍 Scoring...")
        score = await scorer.score(lead)

        print(f"   📊 Score: {score.overall_score}/10 → {score.recommended_action}")

        # Generate email sequence if score >= 7
        if score.overall_score >= 7:
            print("   ✉️  Generating email sequence...")
            sequence = await email_gen.generate_sequence(lead, score)
            print(f"   ✅ Generated {len(sequence.emails)}-email {sequence.sequence_type} sequence")
        else:
            print(f"   ⏸️  Below threshold for auto-sequence (score < 7)")
            sequence = None

        results.append({
            "lead": lead.model_dump(),
            "score": score.model_dump(),
            "sequence": sequence.model_dump() if sequence else None
        })

        print("-" * 70)

    # Save results
    output_file = "test_lead_nurture_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved to: {output_file}\n")

    # Summary
    print("📊 SUMMARY:")
    print(f"   Total leads processed: {len(TEST_LEADS)}")
    high_priority = sum(1 for r in results if r['score']['overall_score'] >= 7)
    print(f"   High priority (7+): {high_priority}")
    print(f"   Auto-sequences generated: {high_priority}")

    print("\n💡 Next steps:")
    print("   1. Review generated email sequences in the JSON file")
    print("   2. Connect to SendGrid/email service for actual sending")
    print("   3. Set up lead intake (webhooks from website/LinkedIn)")
    print("   4. Add tracking for email opens/replies")

if __name__ == "__main__":
    asyncio.run(test_nurture_system())
