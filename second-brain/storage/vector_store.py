"""Vector store interface (Pinecone)"""
from pinecone import Pinecone, ServerlessSpec
from typing import Optional
from shared.config import config
from shared.monitoring import logger
from shared.models import QueryResult

class VectorStore:
    """Manages vector storage in Pinecone"""

    def __init__(self):
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index_name = config.PINECONE_INDEX_NAME
        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        """Check if index exists - manual creation required for free tier"""

        existing = self.pc.list_indexes()

        if self.index_name not in [idx['name'] for idx in existing]:
            raise RuntimeError(
                f"Pinecone index '{self.index_name}' not found. "
                f"Please create it manually at https://app.pinecone.io/ with: "
                f"Name={self.index_name}, Dimensions=1024, Metric=cosine"
            )

    async def upsert(self, id: str, vector: list[float], metadata: dict):
        """Store vector with metadata"""

        try:
            self.index.upsert(vectors=[{
                "id": id,
                "values": vector,
                "metadata": metadata
            }])
            logger.info(f"Upserted vector: {id}")
        except Exception as e:
            logger.error(f"Failed to upsert vector {id}: {e}")
            raise

    async def query(
        self,
        vector: list[float],
        top_k: int = 5,
        filter: Optional[dict] = None,
        include_metadata: bool = True
    ) -> list[QueryResult]:
        """Search for similar vectors"""

        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=include_metadata
            )

            return [
                QueryResult(
                    id=match['id'],
                    score=match['score'],
                    metadata=match.get('metadata', {})
                )
                for match in results['matches']
            ]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Fetch specific vector by ID"""

        try:
            result = self.index.fetch(ids=[id])
            if id in result['vectors']:
                return result['vectors'][id]['metadata']
            return None
        except Exception as e:
            logger.error(f"Failed to fetch {id}: {e}")
            return None

    def get_stats(self) -> dict:
        """Get index statistics"""
        return self.index.describe_index_stats()

# Singleton instance
vector_store = VectorStore()
