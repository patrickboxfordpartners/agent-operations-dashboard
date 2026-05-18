## Integration Hub

The nervous system that connects all 9 agent systems into one unified operating platform.

## What It Does

Turns **9 independent tools** into **one intelligent pipeline**:

1. **Lead → Enrichment → Workflow Analysis → Proposal** (automatic)
2. **Payment → Categorization → Matching → Accounting** (real-time)
3. **Pain Discovery → Content → Leads** (content flywheel)
4. **Cross-system intelligence** (one dashboard, complete picture)

## Architecture

```
┌────────────────────────────────────────────────────┐
│                 Integration Hub                    │
│                                                    │
│  ┌──────────────┐      ┌──────────────┐         │
│  │ Event Bus    │◄────►│ Workflow     │         │
│  │              │      │ Orchestrator │         │
│  └──────────────┘      └──────────────┘         │
│         ▲                      ▲                  │
│         │                      │                  │
│         ▼                      ▼                  │
│  ┌──────────────────────────────────┐            │
│  │      System Adapters              │            │
│  ├──────────────────────────────────┤            │
│  │ • Lead Enrichment                 │            │
│  │ • Workflow Auditor                │            │
│  │ • Proposal Builder                │            │
│  │ • Mercury Intelligence            │            │
│  │ • Lead Nurture                    │            │
│  │ • Content Engine                  │            │
│  │ • Pain Scanner                    │            │
│  │ • Second Brain                    │            │
│  └──────────────────────────────────┘            │
└────────────────────────────────────────────────────┘
```

## Key Workflows

### 1. Lead-to-Proposal (Automated)

**Trigger**: New lead enters system (form, LinkedIn, referral)

**Flow**:
```
New Lead
    ↓
Lead Enrichment
  • Pull company data
  • Score (0-100)
  • Grade (A-F)
    ↓
Grade A/B? → Yes
    ↓
Workflow Auditor
  • Analyze current process
  • Generate solutions (3 tiers)
  • Calculate ROI
    ↓
Proposal Builder
  • Generate custom proposal
  • Include workflow solutions
  • Personalize with enrichment data
    ↓
Lead Nurture
  • Send proposal via email
  • Track opens/engagement
  • Auto follow-up
    ↓
They sign → Convert to Client
```

**Time**: ~5 minutes (zero manual work)

**Manual alternative**: 4-6 hours per lead

### 2. Payment-to-Accounting (Real-Time)

**Trigger**: Mercury transaction webhook

**Flow**:
```
Mercury Transaction
    ↓
Categorize (Claude)
  • Determine category
  • Confidence score
  • Flag anomalies
    ↓
Client Payment? → Yes
    ↓
Match to Client
  • Find matching client
  • Link to invoice
  • Calculate variance
    ↓
Post to Accounting
  • Auto-post if high confidence
  • Flag for review if low
    ↓
Notifications
  • Slack: "Payment received"
  • Email: Thank you + receipt
  • Dashboard: Update status
```

**Time**: ~2 seconds

**Manual alternative**: 30+ minutes per transaction

### 3. Pain-to-Content-to-Lead (Content Flywheel)

**Trigger**: Pain Scanner finds recurring theme

**Flow**:
```
Pain Scanner
  • Monitor Reddit, forums
  • Extract pain points
  • Score frequency/urgency
    ↓
Content Engine
  • Generate LinkedIn post
  • Generate Twitter thread
  • Generate blog post
    ↓
Publish Content
  • Schedule posts
  • Track engagement
    ↓
Leads Generated
  • People reply/DM
  • Form submissions
    ↓
Back to Lead-to-Proposal workflow
```

## System Adapters

Each adapter wraps an agent system:

**LeadEnrichmentAdapter**
- `enrich_lead(lead_data)` → scores, enriches, generates insights

**WorkflowAuditorAdapter**
- `analyze_workflow(description)` → extracts structure, generates solutions

**ProposalBuilderAdapter**
- `generate_proposal(lead, workflow)` → creates custom proposal

**MercuryIntelligenceAdapter**
- `categorize_transaction(txn)` → categorizes, flags anomalies, matches clients

**More adapters coming:**
- LeadNurtureAdapter
- ContentEngineAdapter
- PainScannerAdapter
- SecondBrainAdapter

## Event System

Events flow through the hub:

**Event Types**:
- `lead.created` → Triggers Lead-to-Proposal
- `lead.enriched` → Updates lead record
- `proposal.sent` → Starts engagement tracking
- `payment.received` → Triggers Payment-to-Accounting
- `anomaly.detected` → Sends alerts
- `content.published` → Tracks performance

**Event Flow**:
```python
Event(
    type="payment.received",
    source_system="mercury-intelligence",
    entity_type="transaction",
    entity_id="txn_123",
    data={...}
)
```

## Canonical Data Models

Hub maintains single source of truth:

**Lead**
- Canonical lead entity
- Aggregates data from all systems
- Tracks through lifecycle (new → enriched → qualified → proposal_sent → won)

**Client**
- Converted leads
- Active projects
- Payment history

**Transaction**
- All financial transactions
- Categorized, matched, posted
- Links to clients/invoices

**Project**
- Active client work
- Phases, milestones
- Financial tracking

## Usage

### Run Lead-to-Proposal Workflow

```python
from core.models import Lead, LeadStatus
from workflows.lead_to_proposal import LeadToProposalWorkflow

# Create lead
lead = Lead(
    id="lead_001",
    status=LeadStatus.NEW,
    email="contact@example.com",
    name="John Smith",
    company="Example Corp",
    source="linkedin"
)

# Run workflow
workflow = LeadToProposalWorkflow()
execution = await workflow.execute(
    lead=lead,
    workflow_description="Their current intake process..."
)

# Check results
print(f"Status: {execution.status}")
print(f"Lead Grade: {lead.enrichment_grade}")
print(f"Proposal ID: {lead.proposal_id}")
```

### Run Payment-to-Accounting Workflow

```python
from workflows.payment_to_accounting import PaymentToAccountingWorkflow

# Mercury transaction webhook
transaction = {
    "id": "txn_001",
    "amount": 5000.00,
    "description": "ACH FROM ACME CORP",
    "date": "2026-04-26T10:00:00Z",
    ...
}

# Process payment
workflow = PaymentToAccountingWorkflow()
execution = await workflow.execute(transaction, known_clients)

# Auto-categorized, matched, posted
```

## Quick Start

### 1. Install

```bash
cd integration-hub
# Dependencies are inherited from individual systems
```

### 2. Test Integration

```bash
python test_integration.py
```

This will:
- Test Lead-to-Proposal workflow
- Test Payment-to-Accounting workflow
- Run health checks on all systems

### 3. Deploy

**Option A: Standalone Service**
```bash
# Run as background service
python hub_server.py
```

**Option B: Serverless**
- Deploy workflows as Lambda functions
- API Gateway for webhooks
- EventBridge for scheduling

**Option C: Docker**
```dockerfile
FROM python:3.11
COPY . /app
CMD ["python", "hub_server.py"]
```

## Configuration

All systems auto-discovered from project structure:

```python
# core/config.py
SYSTEMS = {
    "second-brain": "../second-brain",
    "workflow-auditor": "../workflow-auditor",
    "lead-enrichment": "../lead-enrichment",
    ...
}
```

## Value Delivered

**Before Integration Hub:**
- 9 separate systems
- Manual data transfer between systems
- No visibility across pipeline
- Repetitive data entry
- Slow lead-to-client conversion

**After Integration Hub:**
- One unified pipeline
- Automatic data flow
- Real-time intelligence
- Zero duplicate entry
- 10x faster conversion

**ROI Calculation**:

**Lead-to-Proposal**:
- Before: 4-6 hours/lead
- After: 5 minutes automatic
- Savings: 4+ hours/lead × 20 leads/month = 80 hours/month
- Value: 80 hrs × $150/hr = $12,000/month

**Payment Processing**:
- Before: 30 min/transaction × 300 transactions = 150 hours/month
- After: 2 seconds automatic
- Savings: 150 hours/month
- Value: 150 hrs × $50/hr = $7,500/month

**Total Monthly Value**: $19,500

## Next Steps

**Phase 1: Core Integration** ✓
- Lead-to-Proposal workflow ✓
- Payment-to-Accounting workflow ✓
- System adapters ✓
- Event models ✓

**Phase 2: Persistence**
- SQLite database for entities
- Event log storage
- Workflow execution history
- Analytics data warehouse

**Phase 3: Intelligence Layer**
- Unified dashboard
- Cross-system analytics
- Predictive insights
- Anomaly detection

**Phase 4: Scale**
- Message queue (RabbitMQ/Redis)
- Horizontal scaling
- Multi-tenant support
- Enterprise features

## Files

- `core/models.py` - Canonical data models & events
- `core/config.py` - Hub configuration
- `adapters/system_adapter.py` - System adapters
- `workflows/lead_to_proposal.py` - Lead pipeline
- `workflows/payment_to_accounting.py` - Payment pipeline
- `test_integration.py` - Integration tests

## Monitoring

Track workflow health:

```python
# Health check all systems
health = await workflow.health_check()
for system, online in health.items():
    print(f"{system}: {'✅' if online else '❌'}")
```

## Support

This is the foundation. Build on it:
- Add more workflows
- Connect more systems
- Build intelligence layer
- Deploy as service
