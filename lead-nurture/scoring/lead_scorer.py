"""AI-powered lead scoring"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "second-brain"))

from anthropic import Anthropic
from shared.models import Lead, LeadScore

# Try to import Second Brain for case study references
try:
    from query.search import brain_search
    SECOND_BRAIN_AVAILABLE = True
except ImportError:
    SECOND_BRAIN_AVAILABLE = False

class LeadScorer:
    """Scores leads on AI integration readiness"""

    SCORING_CRITERIA = """
Score leads 1-10 on AI integration readiness using these criteria:

**1-3 (Low Priority):**
- Vague pain points or "just exploring"
- No budget signals or authority
- Not urgent
- Low company maturity for AI

**4-6 (Nurture):**
- Clear pain but unclear on solution
- Budget unclear or needs approval
- Timeline ambiguous
- Some decision authority

**7-8 (Engage Soon):**
- Specific operational pain
- Budget signals present
- Timeline within 3 months
- Decision maker or strong influencer
- Company shows AI readiness

**9-10 (Engage Immediately):**
- Urgent, specific pain costing money now
- Clear budget or authority
- Timeline immediate (weeks)
- Decision maker
- Perfect fit for your solutions
"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def score(self, lead: Lead) -> LeadScore:
        """
        Score a lead on AI integration readiness

        Returns:
            LeadScore with 1-10 rating and analysis
        """

        # Get relevant case studies if Second Brain available
        case_studies = []
        if SECOND_BRAIN_AVAILABLE and lead.vertical:
            try:
                results = await brain_search.search(
                    query=lead.message,
                    vertical=lead.vertical,
                    limit=2
                )
                case_studies = [
                    f"{r['metadata']['client_name']}: {r['metadata']['roi_metric']}"
                    for r in results
                ]
            except:
                pass

        prompt = f"""Score this lead on AI integration readiness (1-10 scale).

{self.SCORING_CRITERIA}

LEAD INFORMATION:
- Name: {lead.name}
- Company: {lead.company or 'Unknown'}
- Vertical: {lead.vertical or 'Unknown'}
- Company Size: {lead.company_size or 'Unknown'}
- Source: {lead.source}

THEIR MESSAGE:
{lead.message}

RELEVANT CASE STUDIES (if applicable):
{chr(10).join(f'- {cs}' for cs in case_studies) if case_studies else 'None available'}

Analyze and return JSON:
{{
  "overall_score": 1-10,
  "pain_clarity": 0-10,
  "budget_likelihood": 0-10,
  "decision_authority": 0-10,
  "ai_readiness": 0-10,
  "urgency": 0-10,
  "reasoning": "2-3 sentence analysis",
  "key_strengths": ["Strength 1", "Strength 2"],
  "concerns": ["Concern 1" or empty if none],
  "recommended_action": "engage_immediately|nurture_sequence|qualify_further|deprioritize",
  "talking_points": ["Point to mention in first call"],
  "relevant_case_studies": {json.dumps(case_studies)}
}}
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-6",
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

        score_data = json.loads(text)

        return LeadScore(
            lead_id=lead.lead_id,
            **score_data
        )

# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Test lead
    test_lead = Lead(
        lead_id="test_001",
        name="John Smith",
        email="john@example.com",
        company="ABC Dental Practice",
        vertical="healthcare",
        company_size="5-10",
        source="website_form",
        message="""
        Hi, I run a small dental practice and we're drowning in manual scheduling.
        Our front desk spends 15+ hours a week on appointments and we still get
        double-bookings. Saw your work with SmileCare and wondering if you could
        help us. Budget is flexible if we can see ROI quickly. Need to fix this
        before our busy season in 2 months.
        """
    )

    async def test():
        scorer = LeadScorer(os.getenv("ANTHROPIC_API_KEY"))
        score = await scorer.score(test_lead)

        print(f"\n📊 LEAD SCORE: {score.overall_score}/10")
        print(f"\n**Recommendation:** {score.recommended_action}")
        print(f"\n**Reasoning:** {score.reasoning}")
        print(f"\n**Key Strengths:**")
        for s in score.key_strengths:
            print(f"  • {s}")

        if score.concerns:
            print(f"\n**Concerns:**")
            for c in score.concerns:
                print(f"  • {c}")

        print(f"\n**Talking Points:**")
        for tp in score.talking_points:
            print(f"  • {tp}")

    asyncio.run(test())
