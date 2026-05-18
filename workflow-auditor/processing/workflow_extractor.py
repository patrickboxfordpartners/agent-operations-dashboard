"""Extract structured workflow from unstructured input"""
import json
import sys
from pathlib import Path

# Add second-brain to path for integration
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "second-brain"))

from anthropic import Anthropic
from shared.config import config
from shared.models import WorkflowAnalysis

class WorkflowExtractor:
    """Extracts structured workflow from text/video transcript"""

    def __init__(self):
        self.claude = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    async def extract(self, content: str, client_name: str, vertical: str) -> WorkflowAnalysis:
        """
        Extract workflow structure from description

        Args:
            content: Transcript or text description
            client_name: Client company name
            vertical: Industry vertical

        Returns:
            Structured WorkflowAnalysis
        """

        prompt = f"""Analyze this workflow description and extract a structured process.

Client context:
- Company: {client_name}
- Vertical: {vertical}

Workflow description:
{content}

Extract and return a JSON object with this structure:
{{
  "workflow_name": "Descriptive name for this workflow",
  "frequency": "How often this happens (e.g., '20-30 times per week')",
  "total_time_per_cycle": <minutes per cycle as a number>,
  "people_involved": ["Role 1", "Role 2"],
  "steps": [
    {{
      "step_number": 1,
      "action": "What happens in this step",
      "performed_by": "Who does it",
      "tool": "What tool/system is used",
      "avg_duration_minutes": <number>,
      "pain_points": ["Specific frustrations or issues"],
      "automation_potential": "low|medium|high|very_high"
    }}
  ],
  "current_cost": {{
    "time_per_week_hours": <number>,
    "hourly_rate": <estimated hourly rate for this role>,
    "weekly_cost": <calculated>,
    "annual_cost": <calculated>
  }}
}}

Be specific and quantify everything. If exact numbers aren't given, make reasonable estimates based on the description.
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        text = response.content[0].text

        # Strip markdown if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        workflow_data = json.loads(text)

        return WorkflowAnalysis(**workflow_data)

# Singleton
extractor = WorkflowExtractor()
