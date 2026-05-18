"""Generate personalized email sequences"""
import json
from anthropic import Anthropic
from shared.models import Lead, LeadScore, EmailSequence

class EmailSequenceGenerator:
    """Generates personalized nurture sequences"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def generate_sequence(
        self,
        lead: Lead,
        score: LeadScore
    ) -> EmailSequence:
        """
        Generate personalized 3-email sequence

        Args:
            lead: Lead information
            score: Lead score with analysis

        Returns:
            EmailSequence with 3 emails
        """

        # Determine sequence type
        if score.overall_score >= 7:
            sequence_type = "high_intent"
            prompt_context = "This is a hot lead. Be direct, offer immediate value."
        elif score.overall_score >= 4:
            sequence_type = "qualification"
            prompt_context = "This lead needs nurturing. Educate and build trust."
        else:
            sequence_type = "re_engagement"
            prompt_context = "Low priority. Stay in touch but don't push."

        prompt = f"""Generate a 3-email nurture sequence for this lead.

LEAD INFO:
- Name: {lead.name}
- Company: {lead.company or 'their company'}
- Vertical: {lead.vertical or 'their industry'}
- Score: {score.overall_score}/10
- Their message: {lead.message[:200]}...

SCORING ANALYSIS:
{score.reasoning}

KEY STRENGTHS TO LEVERAGE:
{chr(10).join(f'- {s}' for s in score.key_strengths)}

TALKING POINTS TO INCLUDE:
{chr(10).join(f'- {tp}' for tp in score.talking_points)}

RELEVANT CASE STUDIES:
{chr(10).join(f'- {cs}' for cs in score.relevant_case_studies) if score.relevant_case_studies else 'None - keep it general'}

SEQUENCE TYPE: {sequence_type}
TONE GUIDANCE: {prompt_context}

Generate 3 emails:

**Email 1 (Send immediately):**
- Acknowledge their specific pain
- Reference their situation specifically
- Offer one quick win or insight
- CTA: Book 15-min "AI Quick Win" audit

**Email 2 (Send 3 days later if no response):**
- Share relevant case study or result
- Address likely objection
- Provide additional value (tip, resource)
- CTA: Simple question to continue conversation

**Email 3 (Send 5 days after Email 2 if no response):**
- Final touchpoint
- "Is this still a priority?" approach
- Leave door open
- CTA: Reply or unsubscribe option

Return JSON:
{{
  "emails": [
    {{
      "email_number": 1,
      "subject": "Subject line",
      "body": "Email body (use {lead.name} for personalization)",
      "send_delay_hours": 0,
      "cta": "Specific call to action"
    }},
    {{
      "email_number": 2,
      "subject": "...",
      "body": "...",
      "send_delay_hours": 72,
      "cta": "..."
    }},
    {{
      "email_number": 3,
      "subject": "...",
      "body": "...",
      "send_delay_hours": 192,
      "cta": "..."
    }}
  ]
}}

Keep emails conversational, specific, and under 150 words each.
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
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

        return EmailSequence(
            lead_id=lead.lead_id,
            sequence_type=sequence_type,
            emails=data["emails"]
        )
