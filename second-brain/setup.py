#!/usr/bin/env python3
"""Simple setup script for Second Brain"""
import sys
import subprocess
from pathlib import Path

def main():
    print("\n🧠 Second Brain Setup\n")

    # Check if we're in a venv
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not activated!")
        print("Run: source .venv/bin/activate")
        sys.exit(1)

    # Install dependencies
    print("📦 Installing dependencies...")
    deps = [
        "anthropic", "voyageai", "pinecone", "fastapi", "uvicorn",
        "pydantic", "python-multipart", "watchdog", "rich", "click",
        "langfuse", "redis", "aiofiles", "python-dotenv"
    ]

    subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + deps, check=True)
    print("✅ Dependencies installed\n")

    # Get API keys
    print("🔑 API Key Setup")
    print("=" * 50)
    print("\nI'll ask for your three API keys.")
    print("They will NOT be displayed as you type (for security).\n")

    import getpass

    print("1. Anthropic API Key (from console.anthropic.com)")
    anthropic_key = getpass.getpass("   Paste key: ").strip()

    print("\n2. Voyage AI API Key (from dash.voyageai.com)")
    voyage_key = getpass.getpass("   Paste key: ").strip()

    print("\n3. Pinecone API Key (from app.pinecone.io)")
    pinecone_key = getpass.getpass("   Paste key: ").strip()

    # Create .env file
    env_content = f"""# API Keys
ANTHROPIC_API_KEY={anthropic_key}
VOYAGE_API_KEY={voyage_key}
PINECONE_API_KEY={pinecone_key}

# Pinecone Configuration
PINECONE_ENVIRONMENT=us-west-2
PINECONE_INDEX_NAME=second-brain

# File Storage
STORAGE_PATH=~/completed-work
KNOWLEDGE_GRAPH_PATH=./storage/knowledge_graph.json

# Quality Thresholds
MIN_COMPLETENESS_SCORE=0.7
MIN_DOCUMENTATION_QUALITY=0.5
DEDUP_SIMILARITY_THRESHOLD=0.85

# Cost Controls
DAILY_SPEND_LIMIT=100.0
ALERT_THRESHOLD=0.8

# Redis
REDIS_URL=redis://localhost:6379
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n✅ .env file created\n")

    # Test configuration
    print("🧪 Testing configuration...")
    from shared.config import config

    errors = config.validate()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)

    print("✅ Configuration valid!\n")

    # Run quickstart
    print("🚀 Running quickstart test...\n")
    print("=" * 50)

    import asyncio
    sys.path.insert(0, str(Path.cwd()))

    from ingestion.processor import ingestor
    from shared.monitoring import logger

    async def test_ingest():
        example_path = Path("example_project")
        if not example_path.exists():
            print("❌ Example project not found")
            return False

        try:
            project_id = await ingestor.process_project(example_path)
            print(f"\n✅ SUCCESS! Project ingested: {project_id}\n")
            print("🔍 Try these commands:")
            print(f"   python -m query.cli search 'dental scheduling'")
            print(f"   python -m query.cli show {project_id}")
            print(f"   python -m query.cli stats\n")
            return True
        except Exception as e:
            print(f"\n❌ Ingestion failed: {e}")
            logger.exception("Setup test failed")
            return False

    success = asyncio.run(test_ingest())

    if success:
        print("🎉 Setup complete! Your Second Brain is ready.\n")
    else:
        print("\n⚠️  Setup completed but test failed. Check the error above.\n")

if __name__ == "__main__":
    main()
