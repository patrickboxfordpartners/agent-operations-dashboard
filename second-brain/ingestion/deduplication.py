"""Deduplication engine to prevent duplicate projects"""
import json
from typing import Optional
from shared.models import DuplicateCheck
from shared.ai_client import ai_client
from shared.config import config
from shared.monitoring import logger
from storage.vector_store import vector_store

class DeduplicationEngine:
    """Prevents duplicate projects from polluting the knowledge base"""

    def __init__(self, threshold: float = None):
        self.threshold = threshold or config.DEDUP_SIMILARITY_THRESHOLD

    async def check_duplicate(self, new_project: dict, embedding: list[float]) -> Optional[DuplicateCheck]:
        """
        Check if project is a duplicate

        Returns DuplicateCheck if duplicate found, None otherwise
        """

        client_name = new_project.get('client_name', '')

        # Search for similar projects from same client
        similar = await vector_store.query(
            vector=embedding,
            top_k=5,
            filter={"client_name": client_name} if client_name else None,
            include_metadata=True
        )

        for match in similar:
            if match.score >= self.threshold:
                logger.warning(f"Potential duplicate found: {match.id} (similarity: {match.score:.3f})")

                # Use Claude to decide: merge, version, or false positive
                decision = await self._analyze_duplicate(new_project, match.metadata)

                return DuplicateCheck(
                    is_duplicate=decision['action'] != 'separate',
                    existing_id=match.id,
                    similarity=match.score,
                    existing_project=match.metadata,
                    action=decision['action']
                )

        return None

    async def _analyze_duplicate(self, new: dict, existing: dict) -> dict:
        """Decide how to handle potential duplicate"""

        prompt = f"""We have two similar project records for the same client.

EXISTING PROJECT:
{json.dumps(existing, indent=2)}

NEW PROJECT:
{json.dumps(new, indent=2)}

Determine the relationship:

A) **merge** - Same project, merge to keep best info from both
B) **version** - Different phases/iterations (keep both, link as v1 → v2)
C) **separate** - Actually different projects (false positive, keep separate)

Return JSON:
{{
  "action": "merge|version|separate",
  "reasoning": "explanation",
  "merged_record": {{...}} (only if action=merge)
}}
"""

        response = await ai_client.complete(
            prompt=prompt,
            model="claude-sonnet-4-6",
            max_tokens=2000,
            response_format="json"
        )

        return response["content"]

# Singleton instance
dedup_engine = DeduplicationEngine()
