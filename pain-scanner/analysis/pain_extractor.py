"""Extract pain points from posts using Claude"""
import json
from anthropic import Anthropic
from shared.models import PainPoint
import uuid

class PainExtractor:
    """Extracts structured pain points from raw posts"""

    EXTRACTION_PROMPT = """You are an AI consultant analyzing posts for automation opportunities.

Extract pain points that could be solved with AI/automation. Focus on:
- Repetitive manual work
- Time-consuming processes
- Operational inefficiencies
- Clear, actionable problems (not vague complaints)

For each pain point, assess:
- How common is this problem?
- How urgent/costly is it?
- What's a realistic AI solution?
- Market size (how many businesses have this problem?)

Be ruthless - only extract pains that are:
1. Specific and actionable
2. Solvable with existing AI tools
3. Worth $1000+ in value to solve
"""

    def __init__(self, anthropic_api_key: str):
        self.claude = Anthropic(api_key=anthropic_api_key)

    async def extract_from_posts(
        self,
        posts: list[dict],
        vertical: str,
        source: str = "reddit"
    ) -> list[PainPoint]:
        """
        Extract pain points from a batch of posts

        Args:
            posts: List of posts with title, body, url
            vertical: Industry vertical
            source: Source type (reddit, rss, etc)

        Returns:
            List of extracted PainPoint objects
        """

        if not posts:
            return []

        # Format posts for Claude
        posts_text = "\n\n".join([
            f"POST {i+1}:\nTitle: {p['title']}\nBody: {p['body'][:500]}\nURL: {p['url']}"
            for i, p in enumerate(posts[:10])  # Limit to 10 posts per batch
        ])

        prompt = f"""{self.EXTRACTION_PROMPT}

VERTICAL: {vertical}
SOURCE: {source}

POSTS TO ANALYZE:
{posts_text}

Extract the top 3 most actionable pain points. For each, return JSON:

{{
  "pain_points": [
    {{
      "title": "Short descriptive title",
      "description": "2-3 sentence description of the pain",
      "evidence_quotes": ["Direct quote from post showing the pain"],
      "frequency": "isolated|uncommon|common|widespread",
      "urgency": "low|medium|high|critical",
      "estimated_market_size": "100s|1000s|10,000+",
      "proposed_solution": "Specific AI automation approach (2-3 sentences)",
      "estimated_build_time": "1-2 weeks|3-4 weeks|2-3 months",
      "estimated_roi": "$X/month savings or X% time reduction",
      "source_url": "URL from the post"
    }}
  ]
}}

If no actionable pain points found, return empty pain_points array.
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

        # Convert to PainPoint objects
        pain_points = []
        for p in data.get("pain_points", []):
            pain_point = PainPoint(
                pain_id=f"pain_{uuid.uuid4().hex[:8]}",
                vertical=vertical,
                source=source,
                **p
            )
            pain_points.append(pain_point)

        return pain_points
