# Quick Start Guide

Get Second Brain running in 5 minutes.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- API keys for:
  - [Anthropic](https://console.anthropic.com/) (Claude)
  - [Voyage AI](https://www.voyageai.com/) (Embeddings)
  - [Pinecone](https://www.pinecone.io/) (Vector DB)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd second-brain
uv sync
```

This installs all dependencies in an isolated environment.

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
PINECONE_API_KEY=...
```

### 3. Ingest Example Project

```bash
uv run python scripts/quickstart.py
```

This will:
- Validate your configuration
- Ingest the example dental scheduling project
- Show you how to search

Expected output:
```
📂 Ingesting example project...
INFO - Processing project from: example_project
INFO - Validating project: SmileCare Dental
INFO - ✅ Project validated: SmileCare Dental (completeness: 0.95)
INFO - ✅ Project ingested successfully: proj_2024_smilecare_scheduling_abc123

✅ Project ingested successfully!
   ID: proj_2024_smilecare_scheduling_abc123

🔍 Try searching:
   brain search "dental scheduling"
   brain show proj_2024_smilecare_scheduling_abc123
```

### 4. Test Searching

```bash
# Basic search
brain search "dental scheduling automation"

# Filter by vertical
brain search "appointment booking" --vertical healthcare

# Show project details
brain show <project_id>

# View stats
brain stats
```

### 5. Ingest Your First Real Project

Create a folder with project materials:

```bash
mkdir -p ~/completed-work/my-first-project

# Add files
echo "Client: ABC Corp
Vertical: retail
Pain: Manual inventory tracking
Solution: Built automated inventory sync..." > ~/completed-work/my-first-project/summary.txt
```

Ingest it:

```bash
uv run python -m second_brain.ingestion.processor ~/completed-work/my-first-project
```

Or start the auto-watcher:

```bash
brain-watch
# Now just drop folders into ~/completed-work/
```

## Common Issues

### "ANTHROPIC_API_KEY is required"

→ You didn't create `.env` or the key is missing. Run:

```bash
cp .env.example .env
# Then edit .env with your keys
```

### "Daily limit exceeded"

→ You've hit the $100/day default limit. To increase:

```bash
# In .env
DAILY_SPEND_LIMIT=200.0
```

### "No module named 'second_brain'"

→ Run commands with `uv run`:

```bash
uv run brain search "..."
```

Or activate the venv:

```bash
source .venv/bin/activate
brain search "..."
```

### Import errors

→ Make sure all `__init__.py` files exist:

```bash
find . -type d -name "second_brain" -o -name "ingestion" -o -name "storage" | xargs -I {} touch {}/__init__.py
```

## What's Next?

1. **Ingest more projects** - Aim for 5-10 to start seeing value
2. **Test search quality** - Try different queries, adjust if needed
3. **Build Workflow Auditor** - Uses Second Brain for similar solutions
4. **Add feedback loops** - Track which queries/results are useful (Phase 3)

## Cost Monitoring

Check your spend anytime:

```bash
brain stats
```

Output:
```
📊 Total projects: 5
💰 Today's spend: $2.34 / $100.00 (2%)
💵 Budget remaining: $97.66
```

Logs are in:
- `second-brain.log` - General activity
- `storage/cost_log.jsonl` - Detailed spend tracking

## Architecture Overview

```
You drop folder → Watcher detects it
                     ↓
              Quality validation
                     ↓
              Deduplication check
                     ↓
              Generate embedding
                     ↓
         Store in Pinecone + Knowledge Graph
                     ↓
              Ready for search!
```

## Help

- Read full docs: `second-brain/README.md`
- View architecture: `architecture/01-second-brain-architecture.md`
- Check refinements: `architecture/03-architecture-refinements.md`

## Next: Workflow Auditor

Once Second Brain is working, build the Workflow Auditor which uses it to suggest proven solutions in client audits.

See: `architecture/02-workflow-auditor-architecture.md`
