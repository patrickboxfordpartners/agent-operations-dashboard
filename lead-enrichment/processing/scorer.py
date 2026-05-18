"""AI-powered lead scoring"""
import json
from anthropic import Anthropic

from shared.models import CompanyData, PersonData, EnrichmentScore
from shared.config import config

class LeadScorer:
    """Scores leads based on ICP fit and buying signals"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def score_lead(
        self,
        person: PersonData,
        company: CompanyData,
        icp_context: str = ""
    ) -> EnrichmentScore:
        """
        Score a lead across multiple dimensions

        Args:
            person: Enriched person data
            company: Enriched company data
            icp_context: Optional context about ideal customer

        Returns:
            EnrichmentScore with detailed breakdown
        """

        prompt = f"""You are a lead qualification expert scoring a B2B lead for an AI automation consulting business.

IDEAL CUSTOMER PROFILE:
{icp_context or self._default_icp()}

LEAD DATA:

PERSON:
- Name: {person.full_name}
- Title: {person.title or "Unknown"}
- Department: {person.department or "Unknown"}
- Seniority: {person.seniority_level or "Unknown"}
- Years in role: {person.years_in_role or "Unknown"}
- Years at company: {person.years_at_company or "Unknown"}

COMPANY:
- Name: {company.name}
- Industry: {company.industry or "Unknown"}
- Employees: {company.employee_count or "Unknown"} ({company.employee_range or "Unknown"})
- Revenue: {"$" + f"{company.annual_revenue:,}" if company.annual_revenue else "Unknown"} ({company.revenue_range or "Unknown"})
- Founded: {company.founded_year or "Unknown"}
- Location: {company.location or "Unknown"}
- Funding: {company.funding_stage or "Unknown"}{f" (${company.total_funding:,} raised)" if company.total_funding else ""}
{f"- Last funding: {company.last_funding_date}" if company.last_funding_date else ""}

TECH STACK:
{self._format_tech_stack(company.tech_categories)}

Score this lead on a 0-100 scale for each dimension:

1. **ICP FIT SCORES** (0-100 each):
   - company_size_fit: Does employee count match target range?
   - industry_fit: Is this a target industry?
   - tech_stack_fit: Using technologies that indicate they need automation?
   - revenue_fit: Can they afford $5K-15K/month consulting?

2. **BUYING SIGNAL SCORES** (0-100 each):
   - funding_signal: Recent funding = new budget for improvements
   - growth_signal: Rapid growth = scaling pains
   - tech_debt_signal: Old/manual processes = automation opportunity

3. **CONTACT QUALITY SCORES** (0-100 each):
   - decision_maker_score: Can this person buy or influence buying?
   - contact_findability: Easy to reach (LinkedIn active, email verified)?
   - engagement_potential: Likely to respond based on profile?

SCORING GUIDELINES:
- 90-100: Perfect fit, urgent need
- 70-89: Strong fit, good timing
- 50-69: Decent fit, needs nurturing
- 30-49: Poor fit, but possible
- 0-29: Wrong target

Return JSON:
{{
  "company_size_fit": 85,
  "industry_fit": 90,
  "tech_stack_fit": 75,
  "revenue_fit": 80,
  "funding_signal": 60,
  "growth_signal": 70,
  "tech_debt_signal": 65,
  "decision_maker_score": 85,
  "contact_findability": 80,
  "engagement_potential": 75,
  "overall_score": 78,
  "grade": "B",
  "reasoning": "Brief explanation of overall assessment"
}}

IMPORTANT: Grade must be exactly one of: A, B, C, D, F (no plus or minus signs)
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=2000,
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

        # Remove reasoning from data dict before creating model
        reasoning = data.pop("reasoning", "")

        return EnrichmentScore(**data)

    def _default_icp(self) -> str:
        """Default ICP description"""
        return f"""
TARGET COMPANY:
- Employees: {config.TARGET_EMPLOYEE_RANGE[0]}-{config.TARGET_EMPLOYEE_RANGE[1]}
- Revenue: ${config.TARGET_REVENUE_RANGE[0]:,}-${config.TARGET_REVENUE_RANGE[1]:,}
- Industries: {', '.join(config.TARGET_INDUSTRIES)}
- Technologies: {', '.join(config.TARGET_TECHNOLOGIES)}

TARGET CONTACT:
- Titles: {', '.join(config.TARGET_TITLES)}
- Decision-making authority or strong influence
- Pain: Manual processes, team overwhelm, scaling challenges
"""

    def _format_tech_stack(self, tech_categories: dict) -> str:
        """Format tech stack for prompt"""
        if not tech_categories:
            return "No tech stack data available"

        lines = []
        for category, technologies in tech_categories.items():
            lines.append(f"- {category}: {', '.join(technologies)}")
        return "\n".join(lines)

    async def generate_insights(
        self,
        person: PersonData,
        company: CompanyData,
        score: EnrichmentScore
    ) -> dict:
        """
        Generate actionable insights for this lead

        Returns:
            Dict with key_insights, recommended_approach, talking_points
        """

        prompt = f"""Based on this scored lead, generate actionable sales insights.

LEAD:
- {person.full_name}, {person.title} at {company.name}
- {company.employee_count} employees, {company.industry}
- Overall Score: {score.overall_score}/100 (Grade {score.grade})

SCORE BREAKDOWN:
- ICP Fit: Company Size {score.company_size_fit}, Industry {score.industry_fit}, Tech Stack {score.tech_stack_fit}, Revenue {score.revenue_fit}
- Buying Signals: Funding {score.funding_signal}, Growth {score.growth_signal}, Tech Debt {score.tech_debt_signal}
- Contact Quality: Decision Maker {score.decision_maker_score}, Findability {score.contact_findability}, Engagement {score.engagement_potential}

Generate:

1. **Key Insights** (3-5 bullet points):
   - Most important facts about this lead
   - Red flags or green flags
   - Timing considerations

2. **Recommended Approach** (2-3 sentences):
   - How should we reach out?
   - What message/angle?
   - When to reach out?

3. **Talking Points** (3-5 bullet points):
   - Specific pain points to address
   - Value props that resonate
   - Questions to ask

Return JSON:
{{
  "key_insights": ["...", "..."],
  "recommended_approach": "...",
  "talking_points": ["...", "..."]
}}
"""

        response = self.claude.messages.create(
            model=config.MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        return json.loads(text)
