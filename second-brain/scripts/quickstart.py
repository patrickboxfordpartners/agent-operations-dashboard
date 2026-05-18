"""Quick ingestion script for testing"""
import asyncio
import sys
import os
from pathlib import Path

# Add second-brain to path
second_brain_path = Path(__file__).parent.parent
sys.path.insert(0, str(second_brain_path))

# Change to second-brain directory so relative imports work
os.chdir(second_brain_path)

from ingestion.processor import ingestor
from shared.config import config
from shared.monitoring import logger

async def ingest_example():
    """Ingest the example project"""

    example_path = Path(__file__).parent.parent / "example_project"

    if not example_path.exists():
        print(f"❌ Example project not found at: {example_path}")
        return

    print(f"📂 Ingesting example project from: {example_path}")

    try:
        # Validate config
        errors = config.validate()
        if errors:
            print("\n❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            print("\n💡 Copy .env.example to .env and add your API keys\n")
            return

        # Ingest
        project_id = await ingestor.process_project(example_path)

        print(f"\n✅ Project ingested successfully!")
        print(f"   ID: {project_id}")
        print(f"\n🔍 Try searching:")
        print(f"   brain search \"dental scheduling\"")
        print(f"   brain show {project_id}")

    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        logger.exception("Ingestion error")

if __name__ == "__main__":
    asyncio.run(ingest_example())
