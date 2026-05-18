#!/usr/bin/env python3
"""Test proposal builder"""
import asyncio
import os
from dotenv import load_dotenv

from shared.models import (
    ProposalRequest,
    ClientInfo,
    DiscoveryNotes,
    AutomationInputs,
    WebDevInputs
)
from processing.generator import ProposalGenerator
from processing.formatter import ProposalFormatter
from integration.system_integrations import (
    get_mock_workflow_analysis,
    get_mock_solutions,
    get_mock_enriched_lead
)

load_dotenv()

async def test_ai_automation_proposal():
    """Test AI automation consulting proposal"""

    print("\n🤖 Testing AI Automation Proposal\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    # Mock client data
    client = ClientInfo(
        company_name="Smith & Associates Law Firm",
        contact_name="Jennifer Smith",
        contact_email="jennifer@smithlaw.com",
        industry="Legal Services",
        company_size=28,
        website="https://smithlaw.com"
    )

    discovery = DiscoveryNotes(
        pain_points=[
            "Client intake taking 2+ hours per client",
            "Manual conflict checks prone to errors",
            "Engagement letters all manual copy/paste",
            "Data entry consuming 15 hours/week"
        ],
        goals=[
            "Reduce intake time by 50%+",
            "Eliminate conflict check errors",
            "Faster client onboarding",
            "Free up staff time for billable work"
        ],
        budget_range="$10K-$20K",
        timeline_urgency="Want to implement before Q3",
        decision_makers=["Jennifer Smith (Managing Partner)", "Office Manager"],
        current_tools=["Clio", "QuickBooks", "Microsoft 365"],
        notes="28-person law firm, very tech-forward for legal industry. Managing Partner is frustrated with manual processes eating into billable hours. Strong culture fit for automation."
    )

    # Get mock data from other systems
    workflow_analysis = get_mock_workflow_analysis()
    solutions = get_mock_solutions()

    request = ProposalRequest(
        service_type="ai_automation",
        client=client,
        discovery=discovery,
        automation_inputs=AutomationInputs(
            workflow_analysis=workflow_analysis,
            workflow_solutions=solutions
        ),
        brand_name="Boxford Partners",
        include_case_studies=True,
        include_roi=True,
        tone="professional"
    )

    print("\n📋 Generating proposal...")
    generator = ProposalGenerator(api_key)
    proposal = await generator.generate(request)

    # Add case studies
    proposal = await generator.add_case_studies(proposal, max_studies=2)

    print(f"\n✅ Generated Proposal: {proposal.proposal_id}")
    print(f"   Title: {proposal.title}")
    print(f"   Service: {proposal.service_type}")
    print(f"   Client: {proposal.client.company_name}")

    # Format as markdown
    print("\n" + "=" * 70)
    print("PROPOSAL PREVIEW")
    print("=" * 70)

    formatter = ProposalFormatter()
    markdown = formatter.to_markdown(proposal)

    # Print first 100 lines
    lines = markdown.split("\n")
    for line in lines[:100]:
        print(line)

    if len(lines) > 100:
        print(f"\n... [{len(lines) - 100} more lines] ...")

    # Save outputs
    with open("proposal_ai_automation.md", "w") as f:
        f.write(markdown)

    with open("proposal_ai_automation.html", "w") as f:
        f.write(formatter.to_html(proposal))

    with open("proposal_ai_automation.json", "w") as f:
        f.write(formatter.to_json(proposal))

    print("\n" + "=" * 70)
    print("\n💾 Saved:")
    print("   - proposal_ai_automation.md")
    print("   - proposal_ai_automation.html")
    print("   - proposal_ai_automation.json")

async def test_web_dev_proposal():
    """Test web development proposal"""

    print("\n\n🌐 Testing Web Development Proposal\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return

    client = ClientInfo(
        company_name="Riverside Consulting Group",
        contact_name="Michael Chen",
        contact_email="mchen@riversidecg.com",
        industry="Management Consulting",
        company_size=45,
        website="https://riversidecg.com"
    )

    discovery = DiscoveryNotes(
        pain_points=[
            "Website built in 2015, looks outdated",
            "Not mobile-friendly",
            "Page load times 4+ seconds",
            "SEO ranking dropped significantly",
            "No analytics tracking properly"
        ],
        goals=[
            "Modern, professional website",
            "Mobile-first design",
            "Fast page loads",
            "Rank for target keywords",
            "Lead generation focus"
        ],
        budget_range="$15K-$30K",
        timeline_urgency="Want to launch before conference season (8 weeks)",
        decision_makers=["Michael Chen (Founder)", "Marketing Director"],
        current_tools=["WordPress", "Google Analytics", "Mailchimp"],
        notes="Consulting firm doing $5M/year but website doesn't reflect brand quality. Losing leads to competitors with better sites."
    )

    request = ProposalRequest(
        service_type="web_development",
        client=client,
        discovery=discovery,
        webdev_inputs=WebDevInputs(
            site_analysis={
                "url": "https://riversidecg.com",
                "current_tech_stack": ["WordPress 5.8", "jQuery", "Bootstrap 3"],
                "load_time_ms": 4200,
                "mobile_score": 42
            },
            current_tech_stack=["WordPress 5.8", "jQuery", "Bootstrap 3"],
            seo_issues=[
                "Missing meta descriptions on 60% of pages",
                "No structured data markup",
                "Broken internal links",
                "Slow server response time",
                "Not mobile-friendly (Google penalty)"
            ],
            performance_issues=[
                "Large unoptimized images",
                "No CDN",
                "Render-blocking JavaScript",
                "No browser caching"
            ],
            design_requirements="Modern, clean design that reflects premium positioning. Focus on case studies and thought leadership content."
        ),
        brand_name="Boxford Partners"
    )

    print("\n📋 Generating proposal...")
    generator = ProposalGenerator(api_key)
    proposal = await generator.generate(request)
    proposal = await generator.add_case_studies(proposal, max_studies=2)

    print(f"\n✅ Generated Proposal: {proposal.proposal_id}")

    # Save
    formatter = ProposalFormatter()

    with open("proposal_web_dev.md", "w") as f:
        f.write(formatter.to_markdown(proposal))

    with open("proposal_web_dev.html", "w") as f:
        f.write(formatter.to_html(proposal))

    print("\n💾 Saved:")
    print("   - proposal_web_dev.md")
    print("   - proposal_web_dev.html")

async def test_combined_proposal():
    """Test combined (automation + web dev) proposal"""

    print("\n\n🚀 Testing Combined Proposal\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return

    client = ClientInfo(
        company_name="Greenfield Accounting",
        contact_name="Sarah Williams",
        contact_email="sarah@greenfieldcpa.com",
        industry="Accounting",
        company_size=18,
        website="https://greenfieldcpa.com"
    )

    discovery = DiscoveryNotes(
        pain_points=[
            "Website doesn't generate leads",
            "Client onboarding 100% manual",
            "QuickBooks not integrated with CRM",
            "Staff spending 20+ hours/week on admin",
            "Can't scale without hiring"
        ],
        goals=[
            "Professional website that generates leads",
            "Automated client onboarding portal",
            "Integrated systems (QuickBooks, CRM, email)",
            "Grow from 18 to 30 staff without adding admin overhead"
        ],
        budget_range="$25K-$50K",
        timeline_urgency="Q2 priority project",
        current_tools=["QuickBooks Desktop", "Excel", "Gmail", "Old WordPress site"],
        notes="Fast-growing accounting firm. Ready to invest in growth infrastructure. Partners understand tech investment = capacity increase."
    )

    request = ProposalRequest(
        service_type="combined",
        client=client,
        discovery=discovery,
        automation_inputs=AutomationInputs(
            workflow_analysis={
                "workflow_name": "Client Onboarding",
                "total_time_minutes": 180,
                "annual_cost": 36000,
                "frequency_per_month": 12
            }
        ),
        webdev_inputs=WebDevInputs(
            seo_issues=["Poor keyword rankings", "No blog/content"],
            performance_issues=["Slow load times", "Not mobile-optimized"]
        )
    )

    print("\n📋 Generating proposal...")
    generator = ProposalGenerator(api_key)
    proposal = await generator.generate(request)
    proposal = await generator.add_case_studies(proposal, max_studies=1)

    print(f"\n✅ Generated Proposal: {proposal.proposal_id}")

    # Save
    formatter = ProposalFormatter()

    with open("proposal_combined.md", "w") as f:
        f.write(formatter.to_markdown(proposal))

    print("\n💾 Saved: proposal_combined.md")

async def main():
    """Run all proposal tests"""

    await test_ai_automation_proposal()
    await test_web_dev_proposal()
    await test_combined_proposal()

    print("\n\n✅ All proposal types generated!\n")
    print("💡 Next steps:")
    print("   1. Review generated proposals for quality")
    print("   2. Connect to real Workflow Auditor data")
    print("   3. Connect to Lead Enrichment data")
    print("   4. Add PDF export (reportlab/weasyprint)")
    print("   5. Add e-signature integration (DocuSign/PandaDoc)")
    print("   6. Create API endpoint for proposal-agent frontend")
    print("   7. Build approval workflow (review before sending)")
    print("   8. Track proposal metrics (sent, viewed, signed)\n")

if __name__ == "__main__":
    asyncio.run(main())
