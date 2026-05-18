"""Quality validation for ingested projects"""
import json
from typing import Optional
from shared.models import (
    ProjectMetadata,
    CompletenessAssessment,
    QualityScores
)
from shared.ai_client import ai_client
from shared.config import config
from shared.monitoring import logger

class QualityGate:
    """Validates and enriches projects before storage"""

    def __init__(self):
        self.min_completeness = config.MIN_COMPLETENESS_SCORE
        self.min_documentation = config.MIN_DOCUMENTATION_QUALITY

    async def validate_and_enrich(self, raw_project: dict) -> ProjectMetadata:
        """
        Main validation pipeline:
        1. Assess completeness
        2. Auto-enrich if needed
        3. Score quality dimensions
        4. Return validated ProjectMetadata
        """

        logger.info(f"Validating project: {raw_project.get('client_name', 'unknown')}")

        # Step 1: Assess what we have
        assessment = await self._assess_completeness(raw_project)

        # Step 2: Try to enrich if below threshold
        if assessment.completeness_score < self.min_completeness:
            logger.warning(f"Project below completeness threshold: {assessment.completeness_score:.2f}")

            if assessment.can_auto_enrich:
                logger.info("Attempting auto-enrichment...")
                enriched = await self._auto_enrich(raw_project, assessment.missing_fields)

                # Re-assess
                assessment = await self._assess_completeness(enriched)
                raw_project = enriched

            if assessment.completeness_score < self.min_completeness:
                # Still below threshold
                await self._flag_for_review(raw_project, assessment)
                raise ValueError(
                    f"Project below quality threshold ({assessment.completeness_score:.2f}). "
                    f"Issues: {', '.join(assessment.issues)}"
                )

        # Step 3: Score quality dimensions
        scores = await self._score_project(raw_project)

        if scores.documentation_quality < self.min_documentation:
            logger.warning(f"Low documentation quality: {scores.documentation_quality:.2f}")

        # Step 4: Create validated metadata
        try:
            metadata = ProjectMetadata(
                **raw_project,
                completeness_score=assessment.completeness_score,
                reusability_score=scores.reusability_score,
                documentation_quality=scores.documentation_quality
            )

            logger.info(f"✅ Project validated: {metadata.client_name} "
                       f"(completeness: {metadata.completeness_score:.2f}, "
                       f"reusability: {metadata.reusability_score:.2f})")

            return metadata

        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise

    async def _assess_completeness(self, project: dict) -> CompletenessAssessment:
        """Use Claude to assess what's missing"""

        prompt = f"""Assess this project documentation for completeness.

Required fields:
- client_name
- vertical (healthcare, legal, manufacturing, retail, saas, services, other)
- pain_point (the problem being solved)
- solution_description (what was built)
- date_completed (ISO 8601 format)
- tools_used (list of tools/APIs)

Recommended fields:
- solution_category
- roi_metric (quantified outcome)
- cost_to_build
- monthly_client_savings
- project_duration_hours

Project data:
{json.dumps(project, indent=2)}

Assess:
1. Are all required fields present and meaningful (not empty/generic)?
2. What recommended fields are missing?
3. Can missing information be reasonably inferred from what's present?

Return JSON:
{{
  "completeness_score": 0.0-1.0,
  "missing_fields": ["field1", "field2"],
  "issues": ["specific issue descriptions"],
  "can_auto_enrich": true/false,
  "reasoning": "explanation of score"
}}
"""

        response = await ai_client.complete(
            prompt=prompt,
            model="claude-sonnet-4-6",
            max_tokens=1000,
            response_format="json"
        )

        return CompletenessAssessment(**response["content"])

    async def _auto_enrich(self, project: dict, missing_fields: list[str]) -> dict:
        """Try to fill missing fields from context"""

        prompt = f"""This project is missing: {', '.join(missing_fields)}

Can you infer these from the existing information? Use reasonable assumptions based on:
- Industry standards (e.g., typical hourly rates for SMB consulting)
- Project scope (estimate duration from solution complexity)
- Tools mentioned (infer solution_category from tools)

Existing data:
{json.dumps(project, indent=2)}

Return the FULL project object with missing fields filled in (or null if unknowable).
DO NOT change existing fields. Only add/infer missing ones.

Return as JSON matching the input structure.
"""

        response = await ai_client.complete(
            prompt=prompt,
            model="claude-sonnet-4-6",
            max_tokens=2000,
            response_format="json"
        )

        return response["content"]

    async def _score_project(self, project: dict) -> QualityScores:
        """Score reusability and documentation quality"""

        prompt = f"""Score this project on two dimensions (0.0-1.0):

1. **Reusability**: How applicable is this solution to other clients?
   - 1.0 = Pattern works across verticals with minimal changes (e.g., scheduling automation)
   - 0.7 = Works within same vertical with customization (e.g., HIPAA-compliant intake)
   - 0.4 = Requires significant adaptation (e.g., custom integration with proprietary system)
   - 0.0 = Highly specific to this one client (e.g., one-time data migration)

2. **Documentation Quality**: How well-documented is the solution?
   - 1.0 = Complete: architecture, tools, prompts, outcomes, lessons learned
   - 0.7 = Good: clear description, tools, outcomes documented
   - 0.4 = Adequate: basic description, some details missing
   - 0.0 = Poor: minimal info, hard to reconstruct

Project:
{json.dumps(project, indent=2)}

Return JSON:
{{
  "reusability_score": 0.0-1.0,
  "documentation_quality": 0.0-1.0,
  "reasoning": "brief explanation"
}}
"""

        response = await ai_client.complete(
            prompt=prompt,
            model="claude-sonnet-4-6",
            max_tokens=800,
            response_format="json"
        )

        return QualityScores(**response["content"])

    async def _flag_for_review(self, project: dict, assessment: CompletenessAssessment):
        """Save project for manual review"""

        from pathlib import Path

        review_dir = Path("storage/flagged_for_review")
        review_dir.mkdir(parents=True, exist_ok=True)

        review_file = review_dir / f"{project.get('client_name', 'unknown')}_{assessment.completeness_score:.2f}.json"

        with open(review_file, 'w') as f:
            json.dump({
                "project": project,
                "assessment": assessment.model_dump(),
                "flagged_at": __import__('datetime').datetime.now().isoformat()
            }, f, indent=2)

        logger.warning(f"Project flagged for manual review: {review_file}")

# Singleton instance
quality_gate = QualityGate()
