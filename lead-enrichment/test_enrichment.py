#!/usr/bin/env python3
"""Test lead enrichment"""
import asyncio
import json
import os
from dotenv import load_dotenv
from datetime import datetime

from shared.models import RawLead, EnrichmentStats
from processing.enricher import LeadEnricher

load_dotenv()

# Test leads (mix of quality)
TEST_LEADS = [
    RawLead(
        id="lead_001",
        email="john.smith@acmecorp.com",
        name="John Smith",
        title="VP of Operations",
        source="linkedin"
    ),
    RawLead(
        id="lead_002",
        email="sarah.johnson@techstartup.io",
        name="Sarah Johnson",
        company="TechStartup.io",
        source="referral"
    ),
    RawLead(
        id="lead_003",
        email="mike.brown@locallaw.com",
        name="Mike Brown",
        title="Office Manager",
        company="Local Law Firm",
        source="form"
    ),
    RawLead(
        id="lead_004",
        email="emily.davis@bigcorp.com",
        name="Emily Davis",
        title="IT Manager",
        source="linkedin"
    ),
    RawLead(
        id="lead_005",
        email="alex.martinez@solopreneur.com",
        name="Alex Martinez",
        title="Founder",
        company="Solo Consulting",
        source="form"
    )
]

async def test_enrichment():
    """Test lead enrichment pipeline"""

    print("\n🔍 Testing Lead Enrichment & Scoring\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    # ICP Context
    icp_context = """
We sell AI automation consulting to:
- Professional services firms (consulting, legal, accounting)
- 10-500 employees
- $1M-$50M revenue
- Pain: Manual processes, team overwhelmed, scaling challenges
- Budget: $5K-$15K/month for automation projects

Best contacts: COO, VP Ops, Office Manager, Practice Manager
Green flags: Recent funding, rapid growth, using modern tech stack
Red flags: Too small (<10 employees), too large (>500), wrong industry
"""

    print("\n📋 RAW LEADS:")
    print("=" * 70)
    for lead in TEST_LEADS:
        print(f"\n{lead.name} ({lead.email})")
        print(f"   Title: {lead.title or 'Unknown'}")
        print(f"   Company: {lead.company or 'Unknown'}")
        print(f"   Source: {lead.source}")

    # Enrich leads
    print("\n" + "=" * 70)
    print("🧠 ENRICHING LEADS...")
    print("=" * 70)

    enricher = LeadEnricher(api_key)

    start_time = datetime.now()
    enriched_leads = await enricher.batch_enrich(TEST_LEADS, icp_context)
    duration = (datetime.now() - start_time).total_seconds()

    # Display results
    print("\n✅ ENRICHMENT COMPLETE\n")

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    total_cost = 0.0
    confidence_sum = 0.0
    company_data_found = 0
    tech_stack_found = 0
    funding_data_found = 0

    for enriched in sorted(enriched_leads, key=lambda x: x.score.overall_score, reverse=True):
        lead = enriched.raw_lead
        person = enriched.person
        company = enriched.company
        score = enriched.score

        grade_counts[score.grade] += 1
        total_cost += enriched.cost_usd
        confidence_sum += enriched.enrichment_confidence

        if company and company.industry:
            company_data_found += 1
        if company and len(company.technologies) > 0:
            tech_stack_found += 1
        if company and company.funding_stage:
            funding_data_found += 1

        # Display lead
        grade_icon = {
            "A": "🌟",
            "B": "✅",
            "C": "⚠️",
            "D": "❌",
            "F": "🚫"
        }[score.grade]

        print(f"\n{grade_icon} GRADE {score.grade} ({score.overall_score}/100)")
        print("=" * 70)

        print(f"\n👤 {person.full_name}")
        print(f"   {person.title or 'Unknown Title'} at {company.name if company else 'Unknown Company'}")
        print(f"   {person.email}")
        print(f"   Seniority: {person.seniority_level or 'Unknown'} | Years in role: {person.years_in_role or '?'}")

        if company:
            print(f"\n🏢 {company.name}")
            print(f"   Industry: {company.industry or 'Unknown'}")
            print(f"   Size: {company.employee_count or '?'} employees ({company.employee_range or 'Unknown'})")
            print(f"   Revenue: {company.revenue_range or 'Unknown'}")
            print(f"   Location: {company.location or 'Unknown'}")
            if company.funding_stage:
                funding_text = f"{company.funding_stage}"
                if company.total_funding:
                    funding_text += f" (${company.total_funding:,} raised)"
                print(f"   Funding: {funding_text}")

            if company.technologies:
                print(f"\n💻 Tech Stack:")
                for category, techs in company.tech_categories.items():
                    print(f"   {category}: {', '.join(techs)}")

        print(f"\n📊 SCORES:")
        print(f"   ICP Fit: Size {score.company_size_fit}, Industry {score.industry_fit}, Tech {score.tech_stack_fit}, Revenue {score.revenue_fit}")
        print(f"   Buying Signals: Funding {score.funding_signal}, Growth {score.growth_signal}, Tech Debt {score.tech_debt_signal}")
        print(f"   Contact Quality: Decision Maker {score.decision_maker_score}, Findable {score.contact_findability}, Engagement {score.engagement_potential}")

        print(f"\n💡 KEY INSIGHTS:")
        for insight in enriched.key_insights:
            print(f"   • {insight}")

        print(f"\n📧 RECOMMENDED APPROACH:")
        print(f"   {enriched.recommended_approach}")

        print(f"\n🎯 TALKING POINTS:")
        for point in enriched.talking_points:
            print(f"   • {point}")

        print(f"\n📈 Enrichment Confidence: {enriched.enrichment_confidence:.0%}")
        print(f"💰 Cost: ${enriched.cost_usd:.2f}")

    # Statistics
    print("\n" + "=" * 70)
    print("📊 ENRICHMENT STATISTICS")
    print("=" * 70)

    stats = EnrichmentStats(
        total_leads=len(TEST_LEADS),
        enriched=len(enriched_leads),
        failed=len(TEST_LEADS) - len(enriched_leads),
        grade_a=grade_counts["A"],
        grade_b=grade_counts["B"],
        grade_c=grade_counts["C"],
        grade_d=grade_counts["D"],
        grade_f=grade_counts["F"],
        avg_confidence=confidence_sum / len(enriched_leads) if enriched_leads else 0,
        company_data_found=company_data_found,
        tech_stack_found=tech_stack_found,
        funding_data_found=funding_data_found,
        total_cost_usd=total_cost,
        avg_cost_per_lead=total_cost / len(enriched_leads) if enriched_leads else 0,
        duration_seconds=duration
    )

    print(f"\nTotal Leads: {stats.total_leads}")
    print(f"Enriched: {stats.enriched}")
    print(f"Failed: {stats.failed}")

    print(f"\n📊 Grade Distribution:")
    print(f"   A (90-100): {stats.grade_a} leads")
    print(f"   B (70-89):  {stats.grade_b} leads")
    print(f"   C (50-69):  {stats.grade_c} leads")
    print(f"   D (30-49):  {stats.grade_d} leads")
    print(f"   F (0-29):   {stats.grade_f} leads")

    print(f"\n📈 Data Quality:")
    print(f"   Avg Confidence: {stats.avg_confidence:.0%}")
    print(f"   Company Data Found: {stats.company_data_found}/{stats.enriched}")
    print(f"   Tech Stack Found: {stats.tech_stack_found}/{stats.enriched}")
    print(f"   Funding Data Found: {stats.funding_data_found}/{stats.enriched}")

    print(f"\n💰 Cost Analysis:")
    print(f"   Total Cost: ${stats.total_cost_usd:.2f}")
    print(f"   Cost Per Lead: ${stats.avg_cost_per_lead:.2f}")
    print(f"   Duration: {stats.duration_seconds:.1f}s")

    # Save results
    print("\n" + "=" * 70)

    output_file = "enriched_leads.json"
    with open(output_file, 'w') as f:
        json.dump(
            {
                "leads": [
                    {
                        "raw": {
                            "id": el.raw_lead.id,
                            "email": el.raw_lead.email,
                            "name": el.raw_lead.name
                        },
                        "person": {
                            "name": el.person.full_name,
                            "title": el.person.title,
                            "seniority": el.person.seniority_level
                        },
                        "company": {
                            "name": el.company.name if el.company else None,
                            "industry": el.company.industry if el.company else None,
                            "employees": el.company.employee_count if el.company else None,
                            "revenue_range": el.company.revenue_range if el.company else None,
                            "technologies": el.company.technologies if el.company else []
                        } if el.company else None,
                        "score": {
                            "overall": el.score.overall_score,
                            "grade": el.score.grade
                        },
                        "insights": {
                            "key_insights": el.key_insights,
                            "approach": el.recommended_approach,
                            "talking_points": el.talking_points
                        },
                        "confidence": el.enrichment_confidence,
                        "cost": el.cost_usd
                    }
                    for el in enriched_leads
                ],
                "stats": {
                    "total": stats.total_leads,
                    "enriched": stats.enriched,
                    "grades": {
                        "A": stats.grade_a,
                        "B": stats.grade_b,
                        "C": stats.grade_c,
                        "D": stats.grade_d,
                        "F": stats.grade_f
                    },
                    "avg_confidence": stats.avg_confidence,
                    "total_cost": stats.total_cost_usd
                }
            },
            f,
            indent=2
        )

    print(f"\n💾 Saved results to: {output_file}")

    print("\n✅ Lead enrichment complete!\n")
    print("💡 Next steps:")
    print("   1. Connect real enrichment APIs (Clearbit, Apollo, BuiltWith)")
    print("   2. Set up CRM integration (push enriched leads to Salesforce/HubSpot)")
    print("   3. Create prioritization workflow (A/B leads to sales, C/D to nurture)")
    print("   4. Schedule daily enrichment runs")
    print("   5. Feed high-scoring leads into Lead Nurture system")
    print("   6. Build dashboard to track conversion by grade")
    print("   7. A/B test different ICP criteria\n")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
