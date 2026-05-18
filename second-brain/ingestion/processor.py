"""Main project ingestion pipeline"""
import json
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from shared.models import ProjectMetadata
from shared.ai_client import ai_client
from shared.monitoring import logger
from storage.vector_store import vector_store
from storage.knowledge_graph import knowledge_graph
from ingestion.quality_gate import quality_gate
from ingestion.deduplication import dedup_engine

class ProjectIngestor:
    """Orchestrates project ingestion with quality gates"""

    async def process_project(self, folder_path: Path) -> str:
        """
        Main ingestion workflow:
        1. Read project materials
        2. Extract metadata with Claude
        3. Validate quality
        4. Check for duplicates
        5. Generate embeddings
        6. Store in vector DB + knowledge graph
        """

        logger.info(f"Processing project from: {folder_path}")

        # Step 1: Read folder contents
        content = await self._read_folder(folder_path)

        if not content:
            raise ValueError(f"No readable content found in {folder_path}")

        # Step 2: Extract structured metadata
        raw_metadata = await self._extract_metadata(content, folder_path)

        # Step 3: Quality validation
        try:
            validated_metadata = await quality_gate.validate_and_enrich(raw_metadata)
        except ValueError as e:
            logger.error(f"Quality validation failed: {e}")
            raise

        # Step 4: Generate summary for embedding
        summary = self._create_summary(validated_metadata)

        # Step 5: Generate embedding
        embedding = await ai_client.embed_single(summary)

        # Step 6: Check for duplicates
        duplicate_check = await dedup_engine.check_duplicate(
            validated_metadata.model_dump(),
            embedding
        )

        if duplicate_check and duplicate_check.is_duplicate:
            logger.warning(f"Duplicate detected: {duplicate_check.action}")

            if duplicate_check.action == "merge":
                # Update existing record
                project_id = duplicate_check.existing_id
                logger.info(f"Merging with existing project: {project_id}")
                # TODO: Implement merge logic
            elif duplicate_check.action == "version":
                # Create as new version
                project_id = self._generate_id(validated_metadata)
                logger.info(f"Creating as new version: {project_id}")
            else:
                # False positive, continue as new
                project_id = self._generate_id(validated_metadata)
        else:
            project_id = self._generate_id(validated_metadata)

        # Step 7: Store in vector DB
        await vector_store.upsert(
            id=project_id,
            vector=embedding,
            metadata=validated_metadata.model_dump()
        )

        # Step 8: Update knowledge graph
        await self._update_knowledge_graph(project_id, validated_metadata)

        logger.info(f"✅ Project ingested successfully: {project_id}")
        return project_id

    async def _read_folder(self, folder_path: Path) -> str:
        """Read all text files in folder"""

        content_parts = []

        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.json']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content_parts.append(f"=== {file_path.name} ===\n{content}\n")
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")

        return "\n".join(content_parts)

    async def _extract_metadata(self, content: str, folder_path: Path) -> dict:
        """Use Claude to extract structured metadata from project materials"""

        prompt = f"""Analyze this completed client project and extract structured metadata.

Project materials:
{content[:8000]}  # Truncate if very long

Extract the following fields:

**Required:**
- client_name: The client's company/organization name
- vertical: Industry (healthcare, legal, manufacturing, retail, saas, services, education, real_estate, other)
- pain_point: The core problem being solved (1-2 sentences)
- solution_description: What was built (2-3 sentences)
- date_completed: When the project finished (ISO 8601 format, estimate if not explicit)

**Recommended:**
- tools_used: List of tools/APIs used (e.g., ["Make.com", "Claude API", "Google Calendar"])
- solution_category: Type of solution (workflow_automation, data_analysis, customer_service, etc.)
- roi_metric: Quantified outcome (e.g., "68% time reduction", "$4,800/month savings")
- cost_to_build: Your cost to build (estimate if not stated)
- monthly_client_savings: Client's monthly savings
- project_duration_hours: Hours spent building

Return as JSON matching this structure. Use null for unknown fields.
"""

        response = await ai_client.complete(
            prompt=prompt,
            model="claude-sonnet-4-6",
            max_tokens=2000,
            response_format="json"
        )

        metadata = response["content"]
        metadata['file_path'] = str(folder_path)

        return metadata

    def _create_summary(self, metadata: ProjectMetadata) -> str:
        """Create text summary for embedding"""

        return f"""Client: {metadata.client_name}
Vertical: {metadata.vertical}
Pain Point: {metadata.pain_point}
Solution: {metadata.solution_description}
Tools: {', '.join(metadata.tools_used)}
Outcome: {metadata.roi_metric or 'Not specified'}
Category: {metadata.solution_category or 'General'}
"""

    def _generate_id(self, metadata: ProjectMetadata) -> str:
        """Generate unique project ID"""

        # Format: proj_YYYY_clientname_keyword
        year = metadata.date_completed[:4] if metadata.date_completed else datetime.now().year
        client = metadata.client_name.lower().replace(' ', '')[:15]
        keyword = metadata.solution_category or 'project'

        return f"proj_{year}_{client}_{keyword}_{uuid.uuid4().hex[:6]}"

    async def _update_knowledge_graph(self, project_id: str, metadata: ProjectMetadata):
        """Update knowledge graph with entities and relationships"""

        # Add client entity
        client_id = f"client_{metadata.client_name.lower().replace(' ', '_')}"
        knowledge_graph.add_entity("clients", {
            "id": client_id,
            "name": metadata.client_name,
            "vertical": metadata.vertical
        })

        # Add pain point entity
        pain_id = f"pain_{uuid.uuid4().hex[:8]}"
        knowledge_graph.add_entity("pain_points", {
            "id": pain_id,
            "description": metadata.pain_point,
            "vertical": metadata.vertical
        })

        # Add solution entity
        solution_id = f"sol_{uuid.uuid4().hex[:8]}"
        knowledge_graph.add_entity("solutions", {
            "id": solution_id,
            "name": metadata.solution_category or "Custom Solution",
            "description": metadata.solution_description,
            "tools": metadata.tools_used,
            "reusability_score": metadata.reusability_score
        })

        # Add tool entities
        for tool in metadata.tools_used:
            tool_id = f"tool_{tool.lower().replace(' ', '_').replace('.', '')}"
            knowledge_graph.add_entity("tools", {
                "id": tool_id,
                "name": tool
            })

            # Link solution → tool
            knowledge_graph.add_relationship(solution_id, tool_id, "USES_TOOL")

        # Add relationships
        knowledge_graph.add_relationship(client_id, pain_id, "HAS_PAIN")
        knowledge_graph.add_relationship(pain_id, solution_id, "SOLVED_BY", {
            "project_id": project_id,
            "roi": metadata.roi_metric,
            "date": metadata.date_completed
        })

# Singleton instance
ingestor = ProjectIngestor()
