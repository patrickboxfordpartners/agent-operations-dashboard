"""AI-powered content generation"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "second-brain"))

from anthropic import Anthropic
from shared.models import ContentRequest, GeneratedContent

# Try to import Second Brain for case studies
try:
    from query.search import brain_search
    SECOND_BRAIN_AVAILABLE = True
except ImportError:
    SECOND_BRAIN_AVAILABLE = False

class ContentGenerator:
    """Generates marketing content from your expertise"""

    CONTENT_TEMPLATES = {
        "linkedin_post": {
            "max_length": 1300,
            "format": """Hook (1 line - grab attention)

Main content (3-5 short paragraphs)
- Use line breaks
- Easy to scan
- Specific examples

CTA (clear next step)

Optional: 3-5 relevant hashtags""",
            "tone_guide": "Professional but approachable. Share real results and insights."
        },

        "twitter_thread": {
            "max_length": 280,
            "format": """Tweet 1: Hook + promise
Tweet 2-5: Main points (one per tweet)
Tweet 6: CTA + thread summary

Each tweet: <280 chars, standalone value""",
            "tone_guide": "Punchy, quotable, tactical. Each tweet should work alone."
        },

        "blog_post": {
            "max_length": 1500,
            "format": """# Title (SEO-optimized)

## Introduction (the problem)

## The Challenge (pain point details)

## The Solution (your approach)

## Results (specific outcomes)

## How This Applies to You

## CTA""",
            "tone_guide": "Educational, credible, specific. Show don't tell."
        },

        "email_newsletter": {
            "max_length": 800,
            "format": """Subject line

Brief intro (1-2 sentences)

Main insight or case study

Key takeaway (actionable)

P.S. CTA""",
            "tone_guide": "Conversational, valuable, respectful of time."
        }
    }

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def generate(self, request: ContentRequest) -> GeneratedContent:
        """
        Generate content based on request

        Args:
            request: ContentRequest with topic, type, etc.

        Returns:
            GeneratedContent
        """

        # Get template
        template = self.CONTENT_TEMPLATES[request.content_type]

        # Get case study if specified
        case_study_context = ""
        if request.case_study_id and SECOND_BRAIN_AVAILABLE:
            try:
                from storage.vector_store import vector_store
                case_study = await vector_store.get_by_id(request.case_study_id)
                if case_study:
                    case_study_context = f"""
CASE STUDY TO REFERENCE:
- Client: {case_study.get('client_name')}
- Pain: {case_study.get('pain_point')}
- Solution: {case_study.get('solution_description')}
- Result: {case_study.get('roi_metric')}
- Tools: {', '.join(case_study.get('tools_used', []))}

Use this as the foundation for the content.
"""
            except:
                pass

        prompt = f"""Generate {request.content_type} about: {request.topic}

TARGET AUDIENCE: {request.target_audience}
TONE: {request.tone}

KEY POINTS TO COVER:
{chr(10).join(f'- {kp}' for kp in request.key_points) if request.key_points else 'Extract from case study or general expertise'}

{case_study_context}

FORMAT REQUIREMENTS:
{template['format']}

TONE GUIDANCE:
{template['tone_guide']}

MAX LENGTH: {template['max_length']} characters

IMPORTANT:
- Be specific (use real numbers, tools, outcomes)
- Make it scannable (short paragraphs, bullets where appropriate)
- Include a clear CTA
- Don't use generic platitudes
- {f"Reference the case study naturally" if case_study_context else "Use your AI consulting expertise"}

Return JSON:
{{
  "title": "Title (if applicable)",
  "body": "Full content",
  "metadata": {{
    "hashtags": ["hashtag1", "hashtag2"] (if applicable),
    "cta": "Call to action text",
    "estimated_read_time": "X min" (for blog posts)
  }}
}}
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
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

        return GeneratedContent(
            content_type=request.content_type,
            **data
        )
