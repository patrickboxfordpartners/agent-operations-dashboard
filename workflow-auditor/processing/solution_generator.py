"""Generate automation solutions for workflows"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "second-brain"))

from anthropic import Anthropic
from shared.config import config
from shared.models import WorkflowAnalysis, Solution

class SolutionGenerator:
    """Generates 3 automation solutions (conservative/balanced/aggressive)"""

    def __init__(self):
        self.claude = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    async def generate(
        self,
        workflow: WorkflowAnalysis,
        vertical: str,
        similar_solutions: list = None
    ) -> dict[str, Solution]:
        """
        Generate 3 automation solutions

        Args:
            workflow: Structured workflow analysis
            vertical: Industry vertical
            similar_solutions: Similar projects from Second Brain

        Returns:
            Dict with 3 solutions: conservative, balanced, aggressive
        """

        # Build context from similar solutions
        context = ""
        if similar_solutions:
            context = f"""
PROVEN SOLUTIONS FROM YOUR PAST WORK:
{json.dumps(similar_solutions, indent=2)}

Use these as proof points and reference similar architectures where applicable.
"""

        prompt = f"""Design 3 AI automation solutions for this workflow.

WORKFLOW:
{workflow.model_dump_json(indent=2)}

VERTICAL: {vertical}

{context}

Generate 3 solutions with different automation levels:

1. **CONSERVATIVE** (30-40% automation)
   - Quick wins, minimal risk
   - Focus on obvious pain points
   - Low technical complexity
   - Fast implementation (1-2 weeks)

2. **BALANCED** (60-75% automation)
   - Best ROI/effort ratio
   - Proven patterns and tools
   - Moderate complexity
   - Realistic timeline (3-4 weeks)
   - **This should be your recommended solution**

3. **AGGRESSIVE** (85-95% automation)
   - Maximum automation
   - Higher complexity
   - Longer timeline (6-8 weeks)
   - Only recommend if client has scale

For EACH solution, provide:

{{
  "name": "Descriptive name",
  "description": "2-3 sentence overview",
  "automation_level": 0.3-0.95,
  "architecture": {{
    "diagram": "Text-based flow diagram",
    "tools": ["Specific tools by name"],
    "integration_points": ["What connects to what"]
  }},
  "tools": ["Tool 1", "Tool 2"],
  "estimated_outcomes": {{
    "time_saved_per_cycle_minutes": <number>,
    "new_cycle_time_minutes": <number>,
    "time_savings_percent": <0.0-1.0>,
    "annual_cost_after": <number>,
    "annual_savings": <number>
  }},
  "build_cost": {{
    "your_hours": <estimated hours>,
    "your_rate": 150,
    "your_cost": <calculated>,
    "tool_setup": <one-time costs>,
    "total": <sum>,
    "payback_months": <calculated>
  }},
  "monthly_tool_cost": <ongoing costs>,
  "risks": ["Specific risks"],
  "timeline_weeks": <1-8>
}}

Return JSON:
{{
  "solution_1_conservative": {{...}},
  "solution_2_balanced": {{...}},
  "solution_3_aggressive": {{...}},
  "recommended_solution": "solution_2_balanced",
  "recommendation_reasoning": "Why balanced is best for this case"
}}
"""

        response = self.claude.messages.create(
            model="claude-opus-4-7",  # Use Opus for complex reasoning
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

        solutions_data = json.loads(text)

        # Convert to Solution objects
        result = {}
        for key in ["solution_1_conservative", "solution_2_balanced", "solution_3_aggressive"]:
            if key in solutions_data:
                result[key] = Solution(**solutions_data[key])

        result["recommended_solution"] = solutions_data.get("recommended_solution", "solution_2_balanced")
        result["recommendation_reasoning"] = solutions_data.get("recommendation_reasoning", "")

        return result

# Singleton
generator = SolutionGenerator()
