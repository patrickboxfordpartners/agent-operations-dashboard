# Personal Second Brain + Solution Architect Agent
## Technical Architecture v1.0

---

## System Overview

A RAG-powered knowledge management system that captures, indexes, and retrieves your consulting work. Queryable via natural language, integrates with your development environment, and suggests new solutions based on historical patterns.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      INGESTION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Watch Folder          API Endpoints        Manual Upload        │
│  ~/completed-work/  →  /ingest/project  →   Notion/Airtable    │
│                            ↓                      ↓               │
│                       Metadata Extractor                         │
│                    (Claude: summarize, tag, extract metrics)     │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Vector DB              Knowledge Graph         File Storage     │
│  (Pinecone/Weaviate)    (Neo4j Lite/JSON)     (S3/Local)        │
│  - Embeddings           - Entities:            - Original files  │
│  - Semantic search        • Client              - Recordings     │
│  - Similarity             • Pain point          - Screenshots    │
│                           • Solution            - Deliverables   │
│                           • Tool/API                              │
│                         - Relationships:                          │
│                           • solved_by                             │
│                           • uses_tool                             │
│                           • similar_to                            │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  Claude MCP Server      CLI Tool           IDE Integration       │
│  (Always available)     `brain query`      @brain mention       │
│                            ↓                                      │
│                    Query Router (Claude)                         │
│                    - Semantic search                             │
│                    - Graph traversal                             │
│                    - Hybrid retrieval                            │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  Pattern Analyzer (Nightly Job)                                 │
│  - Finds recurring solutions                                     │
│  - Identifies tool combinations that work                        │
│  - Suggests "productizable" patterns                             │
│  - Flags knowledge gaps                                          │
│                                                                   │
│  Output: Weekly digest + Notion page with opportunities          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Core Components

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Vector DB** | Pinecone (Serverless) | Weaviate Cloud, Qdrant | Pinecone: zero-ops, pay-per-query. Good for <100k vectors |
| **Embeddings** | Voyage AI (voyage-2) | OpenAI text-embedding-3-large | Voyage: 30% better retrieval quality, cheaper |
| **LLM** | Claude Sonnet 4.6 | Claude Opus 4.7 for complex graph queries | Sonnet: speed/cost balance |
| **Knowledge Graph** | JSON-based (start) → Neo4j (scale) | PostgreSQL with pg_graph | JSON: zero setup. Neo4j when you hit ~500 projects |
| **File Storage** | Local filesystem | S3 + CloudFront | Local for MVP, S3 when sharing with agents |
| **Orchestration** | Python + FastAPI | Node.js + Express | Python: better ML libs, easier Claude API usage |
| **Monitoring** | Langfuse | Langsmith, Helicone | Free tier, great for prompt debugging |

### Cost Estimate (Monthly)

```
Pinecone Serverless:     $0 (free tier: 100k vectors)
Voyage AI:               ~$5 (10M tokens embedding)
Claude API:              ~$30 (100k input, 20k output tokens/day)
Hosting (Railway/Fly):   $5
─────────────────────────
Total:                   ~$40/month
```

---

## Data Model

### Vector Store Schema (Pinecone)

```json
{
  "id": "proj_2024_dental_scheduling_automation",
  "values": [0.123, -0.456, ...],  // 1024-dim vector
  "metadata": {
    "type": "project",
    "client": "SmileCare Dental",
    "vertical": "healthcare",
    "pain_point": "manual appointment scheduling",
    "solution_category": "workflow_automation",
    "tools_used": ["make", "claude_api", "google_calendar"],
    "roi_metric": "68% time reduction",
    "date_completed": "2024-03-15",
    "file_path": "s3://brain/projects/2024/dental_scheduling/",
    "cost_to_build": 2400,
    "monthly_client_savings": 4800,
    "project_duration_hours": 16
  }
}
```

### Knowledge Graph Schema (JSON → Neo4j)

```json
{
  "entities": {
    "clients": [
      {
        "id": "client_smilecare",
        "name": "SmileCare Dental",
        "vertical": "healthcare",
        "size": "small",
        "tech_maturity": "low"
      }
    ],
    "pain_points": [
      {
        "id": "pain_manual_scheduling",
        "description": "Manual appointment scheduling taking 15hrs/week",
        "vertical": "multi",
        "frequency": "common"
      }
    ],
    "solutions": [
      {
        "id": "sol_scheduling_automation",
        "name": "AI Scheduling Assistant",
        "pattern": "webhook → claude → calendar API",
        "reusability": "high",
        "proven_rois": [0.68, 0.72, 0.65]
      }
    ],
    "tools": [
      {
        "id": "tool_make",
        "name": "Make.com",
        "category": "no_code_automation",
        "learning_curve": "low"
      }
    ]
  },
  "relationships": [
    {
      "from": "client_smilecare",
      "to": "pain_manual_scheduling",
      "type": "HAS_PAIN"
    },
    {
      "from": "pain_manual_scheduling",
      "to": "sol_scheduling_automation",
      "type": "SOLVED_BY",
      "roi": 0.68,
      "date": "2024-03-15"
    },
    {
      "from": "sol_scheduling_automation",
      "to": "tool_make",
      "type": "USES_TOOL"
    },
    {
      "from": "pain_manual_scheduling",
      "to": "pain_invoice_processing",
      "type": "SIMILAR_TO",
      "confidence": 0.78
    }
  ]
}
```

---

## Implementation Roadmap

### Week 1: MVP Storage + Ingestion

**Day 1-2: Setup**
```bash
# Project structure
mkdir -p second-brain/{ingestion,storage,query,intelligence}
cd second-brain

# Python environment
uv init
uv add anthropic voyageai pinecone-client fastapi uvicorn python-multipart langfuse

# Create watch folder
mkdir ~/completed-work
```

**Day 3-4: Ingestion Pipeline**

File: `ingestion/process_project.py`
```python
import anthropic
import voyageai
from pinecone import Pinecone
from pathlib import Path
import json

class ProjectIngestor:
    def __init__(self):
        self.claude = anthropic.Anthropic()
        self.voyage = voyageai.Client()
        self.pc = Pinecone()
        self.index = self.pc.Index("second-brain")
    
    async def process_project(self, folder_path: Path):
        """Main ingestion workflow"""
        # 1. Read all files
        content = self._read_folder(folder_path)
        
        # 2. Extract metadata with Claude
        metadata = await self._extract_metadata(content)
        
        # 3. Generate embeddings
        embedding = self._embed(metadata['summary'])
        
        # 4. Store in vector DB
        self.index.upsert(vectors=[{
            'id': metadata['id'],
            'values': embedding,
            'metadata': metadata
        }])
        
        # 5. Update knowledge graph
        self._update_graph(metadata)
        
        return metadata['id']
    
    async def _extract_metadata(self, content: str):
        """Use Claude to extract structured metadata"""
        prompt = f"""Analyze this completed client project and extract:
        
1. Client name and vertical (healthcare, legal, manufacturing, etc.)
2. Core pain point (one sentence)
3. Solution category (workflow_automation, data_analysis, customer_service, etc.)
4. Tools/APIs used (list)
5. Quantified outcome (ROI metric)
6. Estimated project hours
7. Key lessons learned

Project materials:
{content}

Return as JSON."""
        
        message = self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(message.content[0].text)
    
    def _embed(self, text: str) -> list[float]:
        """Generate embeddings with Voyage"""
        return self.voyage.embed(
            [text], 
            model="voyage-2"
        ).embeddings[0]
```

**Day 5-7: File Watcher + API**

File: `ingestion/watcher.py`
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

class ProjectWatcher(FileSystemEventHandler):
    def __init__(self, ingestor: ProjectIngestor):
        self.ingestor = ingestor
        self.queue = asyncio.Queue()
    
    def on_created(self, event):
        if event.is_directory:
            # New project folder dropped
            asyncio.create_task(
                self.ingestor.process_project(Path(event.src_path))
            )

# Run as background service
observer = Observer()
observer.schedule(ProjectWatcher(ingestor), path="~/completed-work", recursive=False)
observer.start()
```

### Week 2: Query Interface

**MCP Server** (for Claude Code integration)

File: `query/mcp_server.py`
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("second-brain")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_solutions",
            description="Search past client solutions by pain point, vertical, or outcome",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "vertical": {"type": "string", "optional": True},
                    "min_roi": {"type": "number", "optional": True}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_solutions":
        results = await brain.search(
            query=arguments['query'],
            filters=arguments.get('filters', {})
        )
        
        # Format results for Claude
        formatted = "\n\n".join([
            f"## {r['metadata']['client']} - {r['metadata']['solution_category']}\n"
            f"**Pain:** {r['metadata']['pain_point']}\n"
            f"**ROI:** {r['metadata']['roi_metric']}\n"
            f"**Tools:** {', '.join(r['metadata']['tools_used'])}\n"
            f"**Lessons:** {r['metadata']['lessons_learned']}"
            for r in results[:3]
        ])
        
        return [TextContent(type="text", text=formatted)]
```

Add to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "second-brain": {
      "command": "uv",
      "args": ["run", "~/second-brain/query/mcp_server.py"]
    }
  }
}
```

**CLI Tool**

File: `query/cli.py`
```python
import click
from rich.console import Console
from rich.table import Table

@click.command()
@click.argument('query')
@click.option('--vertical', '-v', help='Filter by vertical')
@click.option('--limit', '-n', default=5, help='Number of results')
def search(query: str, vertical: str, limit: int):
    """Search your second brain"""
    results = brain.search(query, vertical=vertical, limit=limit)
    
    table = Table(title=f"Results for: {query}")
    table.add_column("Client", style="cyan")
    table.add_column("Pain Point", style="yellow")
    table.add_column("ROI", style="green")
    table.add_column("Date", style="blue")
    
    for r in results:
        table.add_row(
            r['client'],
            r['pain_point'][:50],
            r['roi_metric'],
            r['date_completed']
        )
    
    console = Console()
    console.print(table)

if __name__ == '__main__':
    search()
```

### Week 3: Intelligence Layer

**Nightly Pattern Analyzer**

File: `intelligence/pattern_analyzer.py`
```python
async def analyze_patterns():
    """Find productizable patterns across all projects"""
    
    # 1. Get all projects
    all_vectors = index.query(
        vector=[0]*1024,  # dummy vector
        top_k=10000,
        include_metadata=True
    )
    
    # 2. Cluster by solution patterns
    clusters = cluster_solutions(all_vectors)
    
    # 3. Use Claude to identify productizable patterns
    prompt = f"""Analyze these {len(clusters)} solution clusters from my consulting work.

For each cluster, determine:
1. Is this pattern reusable across verticals?
2. What's the common "job to be done"?
3. Could this be a productized offering?
4. What would the next 3 logical variations be?

Clusters:
{json.dumps(clusters, indent=2)}

Return the top 3 product opportunities ranked by:
- Market size (how many businesses have this pain)
- Solution maturity (how proven is this pattern)
- Build effort (how much work to generalize)
"""
    
    insights = await claude.messages.create(
        model="claude-opus-4-7",  # Use Opus for strategic thinking
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 4. Save to Notion
    await notion.pages.create(
        parent={"database_id": INSIGHTS_DB},
        properties={
            "Title": "Weekly Pattern Analysis",
            "Date": datetime.now().isoformat(),
            "Opportunities": insights.content[0].text
        }
    )
```

Run via cron:
```bash
# Add to crontab
0 2 * * 1 cd ~/second-brain && uv run intelligence/pattern_analyzer.py
```

---

## Usage Examples

### Example 1: Query from Claude Code
```
User: @brain what did we build for the dental practice that cut scheduling time 68%?

Brain MCP: [Returns]
## SmileCare Dental - Workflow Automation
**Pain:** Manual appointment scheduling taking 15hrs/week
**ROI:** 68% time reduction (15hrs → 5hrs)
**Tools:** Make.com, Claude API (Haiku), Google Calendar API
**Architecture:**
- Webhook receives appointment requests from website form
- Claude extracts: service type, preferred times, patient history context
- Make checks calendar availability and patient records
- Claude generates confirmation email with personalized tone
- Auto-books if high-confidence, flags for review if ambiguous

**Lessons:**
- Started with full automation, had to add human-in-loop for edge cases
- Haiku sufficient for intent extraction (saved $200/month vs Sonnet)
- Patients loved personalized confirmation emails (NPS +18 points)

**Reusability:** HIGH - same pattern worked for law firm intake (3 implementations, avg 65% time savings)
```

### Example 2: CLI Search
```bash
$ brain query "customer service automation for small teams"

Results for: customer service automation for small teams
┌────────────────┬─────────────────────────────┬─────────────┬────────────┐
│ Client         │ Pain Point                  │ ROI         │ Date       │
├────────────────┼─────────────────────────────┼─────────────┼────────────┤
│ BoutiqueLaw    │ Client intake overwhelm...  │ 58% faster  │ 2024-02-10 │
│ LocalPlumber   │ After-hours calls going ... │ 24/7 cover  │ 2024-03-22 │
│ OnlineRetail   │ Returns processing manual...│ 71% time    │ 2024-01-18 │
└────────────────┴─────────────────────────────┴─────────────┴────────────┘

Run: brain show proj_2024_boutiquelaw_intake
```

---

## Migration Path: JSON → Neo4j

Once you hit ~500 projects or complex graph queries become slow:

```bash
# Setup Neo4j
docker run -p 7474:7474 -p 7687:7687 neo4j:latest

# Migration script
python intelligence/migrate_to_neo4j.py
```

File: `intelligence/migrate_to_neo4j.py`
```python
from neo4j import GraphDatabase

def migrate():
    # Read JSON graph
    with open('storage/knowledge_graph.json') as f:
        graph = json.load(f)
    
    driver = GraphDatabase.driver("bolt://localhost:7687")
    
    with driver.session() as session:
        # Create nodes
        for client in graph['entities']['clients']:
            session.run(
                "CREATE (c:Client {id: $id, name: $name, vertical: $vertical})",
                id=client['id'], name=client['name'], vertical=client['vertical']
            )
        
        # Create relationships
        for rel in graph['relationships']:
            session.run(
                f"MATCH (a {{id: $from}}), (b {{id: $to}}) "
                f"CREATE (a)-[:{rel['type']} {{roi: $roi}}]->(b)",
                from=rel['from'], to=rel['to'], roi=rel.get('roi')
            )
```

---

## Next Steps

1. **Week 1 Goal:** Ingest your first 5 past projects manually
2. **Week 2 Goal:** Query them from Claude Code successfully
3. **Week 3 Goal:** Get first pattern analysis report

Once this is humming, we build the Workflow Auditor which *feeds* this system automatically.
