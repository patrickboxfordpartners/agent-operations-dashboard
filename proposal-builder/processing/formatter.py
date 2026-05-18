"""Proposal formatting and export"""
from shared.models import Proposal

class ProposalFormatter:
    """Formats proposals for different outputs"""

    def to_markdown(self, proposal: Proposal) -> str:
        """
        Export proposal as Markdown

        Args:
            proposal: Proposal object

        Returns:
            Markdown string
        """

        sections = []

        # Cover
        sections.append(f"# {proposal.title}")
        sections.append(f"## {proposal.subtitle}")
        sections.append("")
        sections.append(f"**Prepared for:** {proposal.client.company_name}")
        sections.append(f"**Contact:** {proposal.client.contact_name} ({proposal.client.contact_email})")
        sections.append(f"**Date:** {proposal.created_at[:10]}")
        sections.append(f"**Valid Until:** {proposal.expiration_date}")
        sections.append(f"**Proposal ID:** {proposal.proposal_id}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Executive Summary
        sections.append("## Executive Summary")
        sections.append("")
        sections.append(proposal.executive_summary)
        sections.append("")
        sections.append("---")
        sections.append("")

        # Current State
        sections.append("## Current State Assessment")
        sections.append("")
        sections.append(proposal.current_state_overview)
        sections.append("")

        if proposal.strengths:
            sections.append("### Strengths")
            for strength in proposal.strengths:
                sections.append(f"- ✅ {strength}")
            sections.append("")

        if proposal.challenges:
            sections.append("### Challenges")
            for challenge in proposal.challenges:
                sections.append(f"- ⚠️ {challenge}")
            sections.append("")

        if proposal.opportunities:
            sections.append("### Opportunities")
            for opp in proposal.opportunities:
                sections.append(f"- 💡 {opp}")
            sections.append("")

        sections.append("---")
        sections.append("")

        # Proposed Solution
        sections.append("## Proposed Solution")
        sections.append("")
        sections.append(proposal.solution_overview)
        sections.append("")

        sections.append("### Implementation Phases")
        sections.append("")
        for i, phase in enumerate(proposal.phases, 1):
            sections.append(f"#### Phase {i}: {phase.name}")
            sections.append(f"**Timeline:** {phase.timeline}")
            if phase.dependencies:
                sections.append(f"**Dependencies:** {', '.join(phase.dependencies)}")
            sections.append("")
            sections.append(phase.description)
            sections.append("")
            sections.append("**Deliverables:**")
            for deliverable in phase.deliverables:
                sections.append(f"- {deliverable}")
            sections.append("")

        sections.append("---")
        sections.append("")

        # Pricing
        sections.append("## Investment Options")
        sections.append("")
        for tier in proposal.pricing_tiers:
            recommended = " ⭐ **RECOMMENDED**" if tier.recommended else ""
            sections.append(f"### {tier.name}{recommended}")
            sections.append(f"**{tier.subtitle}**")
            sections.append("")
            sections.append(f"**Investment:** {tier.price_range}")
            sections.append(f"**Timeline:** {tier.timeline}")
            sections.append("")
            sections.append(tier.description)
            sections.append("")
            sections.append("**Included:**")
            for item in tier.included:
                sections.append(f"- ✓ {item}")
            sections.append("")
            if tier.excluded:
                sections.append("**Not Included:**")
                for item in tier.excluded:
                    sections.append(f"- ✗ {item}")
                sections.append("")

        sections.append("**Payment Terms:**")
        sections.append(proposal.payment_terms)
        sections.append("")
        sections.append("---")
        sections.append("")

        # ROI
        if proposal.roi_projection:
            roi = proposal.roi_projection
            sections.append("## Return on Investment")
            sections.append("")
            sections.append(f"- **Time Saved:** {roi.time_saved_per_week} hours/week")
            sections.append(f"- **Annual Cost Savings:** ${roi.cost_savings_annual:,.0f}")
            sections.append(f"- **Annual Revenue Impact:** ${roi.revenue_impact_annual:,.0f}")
            sections.append(f"- **Payback Period:** {roi.payback_months:.1f} months")
            sections.append(f"- **3-Year ROI:** {roi.three_year_roi:.1f}x")
            sections.append("")
            sections.append("---")
            sections.append("")

        # Case Studies
        if proposal.case_studies:
            sections.append("## Success Stories")
            sections.append("")
            for study in proposal.case_studies:
                sections.append(f"### {study.client_name} — {study.industry}")
                sections.append("")
                sections.append(f"**Challenge:** {study.challenge}")
                sections.append("")
                sections.append(f"**Solution:** {study.solution}")
                sections.append("")
                sections.append("**Results:**")
                for result in study.results:
                    sections.append(f"- {result}")
                sections.append("")

            sections.append("---")
            sections.append("")

        # Why Us
        sections.append("## Why Partner With Us")
        sections.append("")
        for reason in proposal.why_us:
            sections.append(f"- {reason}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Next Steps
        sections.append("## Next Steps")
        sections.append("")
        for i, step in enumerate(proposal.next_steps, 1):
            sections.append(f"{i}. {step}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Terms
        sections.append("## Assumptions & Exclusions")
        sections.append("")
        sections.append("### Assumptions")
        for assumption in proposal.assumptions:
            sections.append(f"- {assumption}")
        sections.append("")
        sections.append("### Exclusions")
        for exclusion in proposal.exclusions:
            sections.append(f"- {exclusion}")
        sections.append("")

        return "\n".join(sections)

    def to_html(self, proposal: Proposal) -> str:
        """
        Export proposal as HTML

        Args:
            proposal: Proposal object

        Returns:
            HTML string
        """

        # Convert markdown to HTML (simplified version)
        markdown = self.to_markdown(proposal)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{proposal.title} - {proposal.client.company_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 0.2em; color: #1a1a1a; }}
        h2 {{ font-size: 1.8em; margin-top: 2em; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.3em; margin-top: 1.5em; color: #2c5282; }}
        h4 {{ font-size: 1.1em; margin-top: 1.2em; }}
        ul {{ line-height: 1.8; }}
        hr {{ border: none; border-top: 3px solid #e0e0e0; margin: 3em 0; }}
        .meta {{ color: #666; font-size: 0.9em; }}
        .recommended {{ background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; }}
        strong {{ color: #2c5282; }}
    </style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">
{markdown}
</pre>
</body>
</html>"""

        return html

    def to_json(self, proposal: Proposal) -> str:
        """
        Export proposal as JSON

        Args:
            proposal: Proposal object

        Returns:
            JSON string
        """
        return proposal.model_dump_json(indent=2)
