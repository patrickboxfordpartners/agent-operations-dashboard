"""Search and retrieval logic"""
from typing import Optional, Literal
from shared.ai_client import ai_client
from shared.models import QueryResult
from shared.monitoring import logger
from storage.vector_store import vector_store
from storage.knowledge_graph import knowledge_graph

class BrainSearch:
    """Handles search across vector DB and knowledge graph"""

    async def search(
        self,
        query: str,
        vertical: Optional[str] = None,
        solution_category: Optional[str] = None,
        min_reusability: Optional[float] = None,
        limit: int = 5
    ) -> list[dict]:
        """
        Search for relevant projects

        Args:
            query: Natural language query
            vertical: Filter by industry vertical
            solution_category: Filter by solution type
            min_reusability: Minimum reusability score
            limit: Max results

        Returns:
            List of matching projects with metadata
        """

        logger.info(f"Search query: '{query}' (vertical={vertical}, limit={limit})")

        # Generate query embedding
        query_embedding = await ai_client.embed_single(query)

        # Build filter
        filter_dict = {}
        if vertical:
            filter_dict["vertical"] = vertical
        if solution_category:
            filter_dict["solution_category"] = solution_category
        if min_reusability:
            filter_dict["reusability_score"] = {"$gte": min_reusability}

        # Vector search
        results = await vector_store.query(
            vector=query_embedding,
            top_k=limit * 2,  # Get more than needed for post-filtering
            filter=filter_dict if filter_dict else None
        )

        # Validate relevance
        validated = await self._validate_relevance(query, results, limit)

        logger.info(f"Found {len(validated)} relevant results")
        return validated

    async def _validate_relevance(
        self,
        query: str,
        results: list[QueryResult],
        limit: int
    ) -> list[dict]:
        """Score relevance and potentially refine query"""

        if not results:
            return []

        # Format for Claude
        results_text = []
        for i, r in enumerate(results[:10]):
            results_text.append(f"""
Result {i+1} (score: {r.score:.3f}):
- Client: {r.metadata.get('client_name')}
- Pain: {r.metadata.get('pain_point')}
- Solution: {r.metadata.get('solution_description', '')[:100]}...
- ROI: {r.metadata.get('roi_metric', 'N/A')}
""")

        prompt = f"""User query: "{query}"

Retrieved results:
{''.join(results_text)}

For each result, assess relevance (0.0-1.0):
- 1.0 = Directly answers the query
- 0.5 = Partially relevant
- 0.0 = Not relevant

Return JSON:
{{
  "relevance_scores": [0.9, 0.7, ...],
  "avg_relevance": 0.8,
  "top_k_indices": [0, 2, 4]  # Indices of top {limit} most relevant
}}
"""

        try:
            response = await ai_client.complete(
                prompt=prompt,
                model="claude-sonnet-4-6",
                max_tokens=800,
                response_format="json"
            )

            validation = response["content"]

            # Return top K by relevance
            top_indices = validation.get("top_k_indices", list(range(limit)))[:limit]
            return [results[i].model_dump() for i in top_indices if i < len(results)]

        except Exception as e:
            logger.warning(f"Relevance validation failed: {e}, returning raw results")
            return [r.model_dump() for r in results[:limit]]

    async def get_similar_solutions(self, project_id: str, limit: int = 3) -> list[dict]:
        """Find similar solutions to a given project"""

        # Get project metadata
        project = await vector_store.get_by_id(project_id)
        if not project:
            return []

        # Search using project's pain point
        return await self.search(
            query=project.get('pain_point', ''),
            vertical=project.get('vertical'),
            limit=limit + 1  # +1 because original will be in results
        )

    async def get_by_client(self, client_name: str) -> list[dict]:
        """Get all projects for a client"""

        # Query knowledge graph
        client_entities = knowledge_graph.query("clients", {"name": client_name})

        if not client_entities:
            return []

        # Get relationships
        client_id = client_entities[0]['id']
        relationships = knowledge_graph.get_relationships(client_id, "HAS_PAIN")

        # Fetch full project details from vector store
        projects = []
        for rel in relationships:
            # Traverse pain → solution → project
            solution_rels = knowledge_graph.get_relationships(rel['to'], "SOLVED_BY")
            for sol_rel in solution_rels:
                project_id = sol_rel.get('project_id')
                if project_id:
                    project = await vector_store.get_by_id(project_id)
                    if project:
                        projects.append(project)

        return projects

# Singleton instance
brain_search = BrainSearch()
