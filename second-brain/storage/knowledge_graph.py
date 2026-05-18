"""Knowledge graph storage (JSON-based, upgradeable to Neo4j)"""
import json
from pathlib import Path
from typing import Optional
from shared.config import config
from shared.monitoring import logger

class KnowledgeGraph:
    """Simple JSON-based knowledge graph"""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or config.KNOWLEDGE_GRAPH_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = self._load()

    def _load(self) -> dict:
        """Load graph from disk"""
        if self.path.exists():
            with open(self.path, 'r') as f:
                return json.load(f)

        # Initialize empty graph
        return {
            "entities": {
                "clients": [],
                "pain_points": [],
                "solutions": [],
                "tools": []
            },
            "relationships": []
        }

    def _save(self):
        """Persist graph to disk"""
        with open(self.path, 'w') as f:
            json.dump(self.graph, f, indent=2)
        logger.info(f"Knowledge graph saved: {self.path}")

    def add_entity(self, entity_type: str, entity: dict):
        """Add or update an entity"""

        if entity_type not in self.graph["entities"]:
            self.graph["entities"][entity_type] = []

        # Check if exists
        existing = next(
            (e for e in self.graph["entities"][entity_type] if e.get("id") == entity.get("id")),
            None
        )

        if existing:
            # Update
            idx = self.graph["entities"][entity_type].index(existing)
            self.graph["entities"][entity_type][idx] = entity
            logger.info(f"Updated {entity_type}: {entity.get('id')}")
        else:
            # Add new
            self.graph["entities"][entity_type].append(entity)
            logger.info(f"Added {entity_type}: {entity.get('id')}")

        self._save()

    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Optional[dict] = None):
        """Add a relationship between entities"""

        relationship = {
            "from": from_id,
            "to": to_id,
            "type": rel_type,
            **(properties or {})
        }

        # Check if relationship already exists
        existing = next(
            (r for r in self.graph["relationships"]
             if r["from"] == from_id and r["to"] == to_id and r["type"] == rel_type),
            None
        )

        if not existing:
            self.graph["relationships"].append(relationship)
            logger.info(f"Added relationship: {from_id} -{rel_type}-> {to_id}")
            self._save()

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """Retrieve an entity by ID"""

        if entity_type not in self.graph["entities"]:
            return None

        return next(
            (e for e in self.graph["entities"][entity_type] if e.get("id") == entity_id),
            None
        )

    def get_relationships(self, entity_id: str, rel_type: Optional[str] = None) -> list[dict]:
        """Get all relationships for an entity"""

        results = [
            r for r in self.graph["relationships"]
            if r["from"] == entity_id or r["to"] == entity_id
        ]

        if rel_type:
            results = [r for r in results if r["type"] == rel_type]

        return results

    def query(self, entity_type: str, filters: Optional[dict] = None) -> list[dict]:
        """Query entities with filters"""

        if entity_type not in self.graph["entities"]:
            return []

        entities = self.graph["entities"][entity_type]

        if not filters:
            return entities

        # Simple filtering
        results = []
        for entity in entities:
            match = all(
                entity.get(key) == value
                for key, value in filters.items()
            )
            if match:
                results.append(entity)

        return results

# Singleton instance
knowledge_graph = KnowledgeGraph()
