"""AI-powered proposal generation"""
import json
import uuid
from datetime import datetime, timedelta
from anthropic import Anthropic

from shared.models import (
    ProposalRequest,
    Proposal,
    Phase,
    PricingTier,
    ROIProjection,
    CaseStudy
)
from shared.config import config

class ProposalGenerator:
    """Generates comprehensive proposals for any service type"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def generate(self, request: ProposalRequest) -> Proposal:
        """
        Generate a complete proposal

        Args:
            request: ProposalRequest with all inputs

        Returns:
            Complete Proposal object
        """

        # Build context based on service type
        context = self._build_context(request)

        # Generate proposal content
        proposal_data = await self._generate_content(request, context)

        # Create proposal object
        proposal = Proposal(
            proposal_id=str(uuid.uuid4())[:8],
            service_type=request.service_type,
            client=request.client,
            expiration_date=(datetime.now() + timedelta(days=config.PROPOSAL_EXPIRATION_DAYS)).strftime("%Y-%m-%d"),
            **proposal_data
        )

        return proposal

    def _build_context(self, request: ProposalRequest) -> str:
        """Build context string from all inputs"""

        context_parts = [f"SERVICE TYPE: {request.service_type}"]

        # Client context
        context_parts.append(f"\nCLIENT: {request.client.company_name}")
        if request.client.industry:
            context_parts.append(f"Industry: {request.client.industry}")
        if request.client.company_size:
            context_parts.append(f"Size: {request.client.company_size} employees")

        # Discovery context
        if request.discovery.pain_points:
            context_parts.append(f"\nPAIN POINTS:\n" + "\n".join(f"- {p}" for p in request.discovery.pain_points))
        if request.discovery.goals:
            context_parts.append(f"\nGOALS:\n" + "\n".join(f"- {g}" for g in request.discovery.goals))
        if request.discovery.notes:
            context_parts.append(f"\nDISCOVERY NOTES:\n{request.discovery.notes}")

        # Service-specific context
        if request.service_type in ["ai_automation", "combined"] and request.automation_inputs:
            if request.automation_inputs.workflow_analysis:
                context_parts.append(f"\nWORKFLOW ANALYSIS:\n{json.dumps(request.automation_inputs.workflow_analysis, indent=2)}")
            if request.automation_inputs.workflow_solutions:
                context_parts.append(f"\nPROPOSED SOLUTIONS:\n{json.dumps(request.automation_inputs.workflow_solutions, indent=2)}")

        if request.service_type in ["web_development", "combined"] and request.webdev_inputs:
            if request.webdev_inputs.site_analysis:
                context_parts.append(f"\nWEBSITE ANALYSIS:\n{json.dumps(request.webdev_inputs.site_analysis, indent=2)}")
            if request.webdev_inputs.seo_issues:
                context_parts.append(f"\nSEO ISSUES:\n" + "\n".join(f"- {i}" for i in request.webdev_inputs.seo_issues))

        return "\n".join(context_parts)

    async def _generate_content(self, request: ProposalRequest, context: str) -> dict:
        """Generate proposal content with Claude"""

        pricing_range = config.PRICING_RANGES[request.service_type]

        prompt = f"""Generate a professional consulting proposal for {request.brand_name}.

{context}

Create a proposal with these sections:

1. **Title & Subtitle**
   - Title should reference the specific solution (not generic)
   - Subtitle should highlight the outcome

2. **Executive Summary** (2-3 paragraphs)
   - Hook: Why this matters now
   - Current state assessment
   - Proposed solution and expected outcomes
   - Be specific to their situation

3. **Current State Analysis**
   - Overview paragraph
   - Strengths: 2-4 things they're doing well
   - Challenges: 3-5 specific problems identified
   - Opportunities: 2-3 areas for improvement

4. **Proposed Solution**
   - Overview: 2 paragraphs on the approach
   - Phases: 3-5 implementation phases with:
     * Name
     * Description
     * Deliverables (3-5 specific items)
     * Timeline
     * Dependencies (which phases must come first)

5. **Pricing** (3 tiers)
   - Tier 1: Essential/Foundation ($X,XXX - $XX,XXX)
   - Tier 2: Recommended/Growth ($XX,XXX - $XX,XXX) [mark as recommended]
   - Tier 3: Comprehensive/Transform ($XX,XXX - $XXX,XXX)

   Use these ranges as guidance:
   {json.dumps(pricing_range, indent=2)}

   For each tier:
   - Name, subtitle, price range (min/max), timeline
   - Description (what makes this tier unique)
   - Included (5-8 specific items)
   - Excluded (2-3 items, only for tiers 1-2)

6. **Payment Terms**
   - Standard terms (50% upfront, 25% midpoint, 25% completion)
   - Or monthly retainer structure if applicable

7. **Why {request.brand_name}** (5-7 bullets)
   - Specific value propositions
   - Expertise in their industry/need
   - Track record, methodology, support

8. **ROI Projection** (if enough data)
   - Time saved per week
   - Annual cost savings
   - Annual revenue impact
   - Payback period
   - 3-year ROI

9. **Next Steps** (4-5 steps)
   - Concrete actions
   - Who does what
   - Timelines

10. **Assumptions & Exclusions**
    - Assumptions: 3-5 things assumed to be true
    - Exclusions: 3-5 things explicitly not included

Return JSON:
{{
  "title": "...",
  "subtitle": "...",
  "executive_summary": "...",
  "current_state_overview": "...",
  "strengths": ["...", "..."],
  "challenges": ["...", "..."],
  "opportunities": ["...", "..."],
  "solution_overview": "...",
  "phases": [
    {{
      "name": "...",
      "description": "...",
      "deliverables": ["...", "..."],
      "timeline": "2-3 weeks",
      "dependencies": ["Phase 1"]
    }}
  ],
  "pricing_tiers": [
    {{
      "name": "...",
      "subtitle": "...",
      "price_range": "$X,XXX - $XX,XXX",
      "price_min": 5000,
      "price_max": 15000,
      "timeline": "4-6 weeks",
      "description": "...",
      "included": ["...", "..."],
      "excluded": ["...", "..."],
      "recommended": false
    }}
  ],
  "payment_terms": "...",
  "why_us": ["...", "..."],
  "roi_projection": {{
    "time_saved_per_week": 10.5,
    "cost_savings_annual": 52000,
    "revenue_impact_annual": 25000,
    "payback_months": 3.2,
    "three_year_roi": 4.5
  }},
  "next_steps": ["...", "..."],
  "assumptions": ["...", "..."],
  "exclusions": ["...", "..."]
}}

IMPORTANT:
- Be specific to their situation (reference the context)
- Don't be generic or templated
- Use real numbers from analysis where available
- Pricing should reflect scope and complexity
- Phases should be logical and sequential
- ROI should be conservative and credible
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        text = response.content[0].text
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        data = json.loads(text)

        return data

    async def add_case_studies(
        self,
        proposal: Proposal,
        max_studies: int = 2
    ) -> Proposal:
        """
        Add relevant case studies from Second Brain

        Args:
            proposal: Existing proposal
            max_studies: Maximum number of case studies to include

        Returns:
            Updated proposal with case studies
        """

        # In production, query Second Brain for similar projects
        # For now, use mock data based on service type

        mock_studies = self._get_mock_case_studies(proposal.service_type)
        proposal.case_studies = mock_studies[:max_studies]

        return proposal

    def _get_mock_case_studies(self, service_type: str) -> list[CaseStudy]:
        """Mock case studies"""

        if service_type == "ai_automation":
            return [
                CaseStudy(
                    client_name="Regional Law Firm",
                    industry="Legal Services",
                    challenge="Manual client intake taking 10+ hours/week, errors in data entry",
                    solution="AI-powered intake automation with CRM integration",
                    results=[
                        "Reduced intake time from 10 hours to 1.5 hours (85% savings)",
                        "Zero data entry errors after implementation",
                        "Client satisfaction scores increased 23%",
                        "ROI achieved in 2.8 months"
                    ]
                ),
                CaseStudy(
                    client_name="Dental Practice Group",
                    industry="Healthcare",
                    challenge="Scheduling consuming 15 hours/week, frequent conflicts",
                    solution="AI scheduling assistant with Make.com + Claude integration",
                    results=[
                        "Scheduling time reduced to 5 hours/week (68% savings)",
                        "Appointment conflicts down 92%",
                        "Patient wait times reduced by 40%",
                        "Payback period: 3.4 months"
                    ]
                )
            ]
        elif service_type == "web_development":
            return [
                CaseStudy(
                    client_name="Professional Services Firm",
                    industry="Consulting",
                    challenge="Outdated website, no mobile optimization, poor SEO",
                    solution="Modern Next.js rebuild with CMS and analytics",
                    results=[
                        "Mobile traffic increased 240%",
                        "Organic search traffic up 180% in 6 months",
                        "Lead conversion rate improved 45%",
                        "Page load time reduced from 4.2s to 0.8s"
                    ]
                ),
                CaseStudy(
                    client_name="SaaS Startup",
                    industry="Technology",
                    challenge="Generic template site, no conversion optimization",
                    solution="Custom marketing site with A/B testing and analytics",
                    results=[
                        "Conversion rate increased from 2.1% to 5.8%",
                        "Cost per acquisition decreased 62%",
                        "Demo bookings up 3.5x",
                        "Site ranked #1 for 12 target keywords"
                    ]
                )
            ]
        else:  # combined
            return [
                CaseStudy(
                    client_name="Accounting Firm",
                    industry="Professional Services",
                    challenge="Manual workflows + outdated website limiting growth",
                    solution="Website rebuild + client portal + workflow automation",
                    results=[
                        "New website generated 3.2x more leads",
                        "Client onboarding time reduced 70%",
                        "Partner time saved: 12 hours/week",
                        "Net new revenue: $180K in year one"
                    ]
                )
            ]
