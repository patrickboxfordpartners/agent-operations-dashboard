# Agent Operations Dashboard

AI-powered consulting intelligence system with two core components:

## 🧠 Second Brain
Personal knowledge management system that captures, indexes, and retrieves your consulting work using RAG (Retrieval-Augmented Generation).

**Status:** ✅ Production-ready codebase (MVP + Quality Gates)

[**→ Get Started in 5 Minutes**](QUICKSTART.md)

### Features
- Vector search (Pinecone + Voyage AI)
- Quality validation & auto-enrichment
- Deduplication detection
- Cost tracking & limits
- CLI interface
- Auto-ingestion via file watcher

### Quick Commands
```bash
cd second-brain
uv sync                                    # Install
uv run python scripts/quickstart.py       # Test with example
brain search "scheduling automation"       # Search
brain stats                                # View metrics
```

---

## 📊 Workflow Auditor
Converts client process descriptions into AI integration roadmaps with ROI calculations.

**Status:** 📐 Architecture complete, ready to build

[**→ Read Architecture**](architecture/02-workflow-auditor-architecture.md)

### What It Does
- Ingests Looms/Docs/Text workflow descriptions
- Extracts structured process maps (Claude)
- Generates 3 automation solutions (Conservative/Balanced/Aggressive)
- Outputs client-ready Notion pages with ROI
- References Second Brain for proven solutions

---

## 📚 Documentation

| Document | Description | Status |
|----------|-------------|--------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide | ✅ Complete |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | What we built & why | ✅ Complete |
| [Second Brain Architecture](architecture/01-second-brain-architecture.md) | Complete technical spec (9.5k words) | ✅ Complete |
| [Workflow Auditor Architecture](architecture/02-workflow-auditor-architecture.md) | Complete technical spec (8.2k words) | ✅ Complete |
| [Architecture Refinements](architecture/03-architecture-refinements.md) | Robustness & learning (12k words) | ✅ Complete |

---

## 🚀 Implementation Roadmap

### ✅ Phase 1: Second Brain MVP (Complete)
- [x] Vector storage & search
- [x] Knowledge graph (JSON)
- [x] CLI interface
- [x] Basic ingestion

### ✅ Phase 2: Quality Gates (Complete)
- [x] Input validation
- [x] Auto-enrichment
- [x] Deduplication
- [x] Cost tracking
- [x] Relevance scoring

### 🔄 Phase 3: Workflow Auditor (Next - 1-2 weeks)
1. Make.com intake scenarios
2. FastAPI processing engine
3. Notion output templates
4. Integration with Second Brain
5. Test with 3-5 real prospects

---

## 💰 Monthly Costs

- **Second Brain**: ~$35 (30 projects + 100 queries)
- **Workflow Auditor**: ~$60 (20 audits)
- **Combined**: ~$95/month

**Target ROI (Month 3)**: $15,400 MRR from audits

---

## 🚦 Getting Started

```bash
cd second-brain
cp .env.example .env          # Add your API keys
uv sync                       # Install dependencies
uv run python scripts/quickstart.py  # Test
```

[**→ Full Setup Guide**](QUICKSTART.md)

---

Built with Claude Sonnet 4.6 🤖
