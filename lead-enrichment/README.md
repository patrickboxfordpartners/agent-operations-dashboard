# Lead Enrichment & Scoring

AI-powered lead enrichment that turns email addresses into qualified, scored prospects with actionable insights.

## What It Does

1. **Enriches Leads** - Takes minimal info (email, name), fetches company data, tech stack, funding
2. **Scores** - Multi-dimensional scoring (ICP fit, buying signals, contact quality)
3. **Generates Insights** - AI analyzes data and provides talking points, recommended approach
4. **Prioritizes** - Grades leads A-F so you focus on best opportunities

## Value Proposition

**Time Savings**: 30 min/lead → 2 min/lead (93% reduction)

**Typical Use Case**:
- Sales team with 100 inbound leads/month
- Currently: Manual research on LinkedIn, company websites (30 min each = 50 hrs/month)
- After: Auto-enrichment, review insights only (2 min each = 3.5 hrs/month)
- ROI: 1 month

**What Makes This Different**:
- Multi-source enrichment (company + person + tech + funding)
- AI scoring tailored to your ICP
- Actionable insights, not just data dumps
- Integrates with existing CRM

## Quick Start

### 1. Install Dependencies

```bash
cd lead-enrichment
pip install -e .
```

### 2. Set Up Environment

Create `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...

# Optional (for production enrichment)
CLEARBIT_API_KEY=your_key
APOLLO_API_KEY=your_key
BUILTWITH_API_KEY=your_key
CRUNCHBASE_API_KEY=your_key
```

### 3. Test with Mock Data

```bash
python test_enrichment.py
```

This will:
- Enrich 5 test leads with mock data
- Score each lead (A-F grade)
- Generate insights and talking points
- Show cost and confidence metrics

## Architecture

```
┌─────────────┐
│  Raw Lead   │ (email, name, company)
└──────┬──────┘
       │
       v
┌──────────────────────┐
│  Enrichment Engine   │
├──────────────────────┤
│ • Clearbit           │ → Person data
│ • Apollo.io          │ → B2B database
│ • BuiltWith          │ → Tech stack
│ • Crunchbase         │ → Funding data
└──────┬───────────────┘
       │
       v
┌──────────────────────┐     ┌─────────────┐
│  AI Scorer           │────▶│  ICP Rules  │
│  (Claude)            │     └─────────────┘
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  Enriched Lead       │
│  • Score (0-100)     │
│  • Grade (A-F)       │
│  • Insights          │
│  • Talking points    │
└──────────────────────┘
```

## Scoring Dimensions

### ICP Fit (40% weight)
- **Company Size** - Right number of employees?
- **Industry** - Target vertical?
- **Tech Stack** - Using relevant technologies?
- **Revenue** - Can afford your service?

### Buying Signals (35% weight)
- **Funding** - Recent raise = new budget
- **Growth** - Hiring = scaling pains
- **Tech Debt** - Old systems = automation opportunity

### Contact Quality (25% weight)
- **Decision Maker** - Right title/department?
- **Findability** - Easy to reach?
- **Engagement** - Active on LinkedIn?

### Grading Scale
- **A (90-100)**: Perfect fit, contact immediately
- **B (70-89)**: Strong fit, prioritize
- **C (50-69)**: Decent fit, nurture sequence
- **D (30-49)**: Poor fit, long-term nurture
- **F (0-29)**: Wrong target, disqualify

## Example Output

```
🌟 GRADE A (92/100)
======================================================================

👤 John Smith
   VP of Operations at ACME Corp
   john.smith@acmecorp.com
   Seniority: senior | Years in role: 2

🏢 ACME Corp
   Industry: Professional Services
   Size: 75 employees (51-200)
   Revenue: $5M-$10M
   Location: Austin, TX

💻 Tech Stack:
   CRM: Salesforce, HubSpot
   Accounting: QuickBooks
   Collaboration: Slack, Microsoft 365

📊 SCORES:
   ICP Fit: Size 95, Industry 100, Tech 85, Revenue 90
   Buying Signals: Funding 60, Growth 80, Tech Debt 70
   Contact Quality: Decision Maker 95, Findable 90, Engagement 85

💡 KEY INSIGHTS:
   • Perfect ICP fit - consulting firm in sweet spot (75 employees, $8M revenue)
   • VP Ops with 2 years tenure = established but not stale
   • Modern tech stack shows willingness to invest in tools
   • Growth signal: LinkedIn shows 15% headcount increase last 6 months

📧 RECOMMENDED APPROACH:
   Direct LinkedIn outreach with specific pain point about scaling operations.
   Reference their recent growth and tech stack. Offer 15-min process audit.

🎯 TALKING POINTS:
   • "Noticed you're using Salesforce + HubSpot - optimizing the handoff?"
   • "75 employees is exactly when manual processes break - seen this?"
   • "Recent growth means processes that worked at 50 don't work at 75"
   • "Most consulting firms waste 10-15 hrs/week on manual client intake"
```

## Configuration

### Define Your ICP

Edit `shared/config.py`:

```python
TARGET_EMPLOYEE_RANGE = (10, 500)
TARGET_REVENUE_RANGE = (1_000_000, 50_000_000)
TARGET_INDUSTRIES = ["Professional Services", "Healthcare", ...]
TARGET_TECHNOLOGIES = ["Salesforce", "QuickBooks", ...]
TARGET_TITLES = ["CEO", "COO", "VP Operations", ...]
```

### Adjust Scoring Weights

```python
WEIGHT_ICP_FIT = 0.40
WEIGHT_BUYING_SIGNALS = 0.35
WEIGHT_CONTACT_QUALITY = 0.25
```

## Integration Points

### 1. Enrichment APIs

**Clearbit** ($99-$999/mo):
- Best for: Company + person enrichment
- Data: Firmographics, social profiles, job history

**Apollo.io** ($49-$199/mo):
- Best for: B2B database, email finding
- Data: Company, contact info, job titles

**BuiltWith** ($295-$995/mo):
- Best for: Tech stack detection
- Data: Technologies used by domain

**Crunchbase** ($29-$99/mo):
- Best for: Funding data
- Data: Funding rounds, investors, valuation

### 2. CRM Integration

Push enriched leads to:
- **Salesforce** - Via REST API
- **HubSpot** - Via Contacts API
- **Pipedrive** - Via Persons API

Include custom fields for:
- Enrichment score
- Grade
- Key insights
- Recommended approach

### 3. Lead Nurture

Feed scored leads into:
- **Grade A/B** → Immediate outreach (Lead Nurture high-intent sequence)
- **Grade C** → Nurture drip campaign
- **Grade D** → Long-term newsletter
- **Grade F** → Disqualify

## Cost Analysis

**Per Lead**:
- Clearbit: $0.50
- BuiltWith: $0.10
- Crunchbase: $0.05
- Claude API: $0.08
- Total: ~$0.75/lead

**Monthly** (100 leads):
- Enrichment: $75
- API subscriptions: ~$200
- Total: $275/month

**Labor Savings**:
- Before: 100 leads × 30 min × $50/hr = $2,500/month
- After: 100 leads × 2 min × $50/hr = $165/month
- Savings: $2,335/month

**ROI**: 2 weeks

## Pricing Recommendation

- **Base**: $500/month (up to 100 leads)
- **Volume**: $0.75/lead above 100
- **Enterprise**: Custom pricing for 1,000+ leads/month
- **Add-on**: Custom ICP tuning ($200 one-time)

## Next Steps

1. **Test with mock data** ✓
2. **Connect real enrichment APIs** - Get API keys from Clearbit, Apollo, etc.
3. **Integrate with CRM** - Push enriched leads to Salesforce/HubSpot
4. **Build prioritization workflow** - Route A/B leads to sales, C/D to marketing
5. **Schedule daily runs** - Auto-enrich new leads from CRM
6. **Track conversion by grade** - Validate scoring model
7. **A/B test ICP criteria** - Optimize scoring weights

## Production Deployment

### Daily Workflow

```python
# Fetch new leads from CRM
new_leads = crm.get_leads(status="new")

# Enrich and score
enricher = LeadEnricher(api_key)
enriched = await enricher.batch_enrich(new_leads)

# Route by grade
for lead in enriched:
    if lead.score.grade in ["A", "B"]:
        # Push to sales queue
        crm.assign_to_sales(lead)
        # Trigger Lead Nurture high-intent sequence
        nurture.start_sequence(lead, "high_intent")
    elif lead.score.grade == "C":
        # Marketing nurture
        crm.add_to_campaign(lead, "nurture_sequence")
    else:
        # Long-term nurture or disqualify
        crm.update_status(lead, "low_priority")
```

## Files

- `shared/models.py` - Data models (RawLead, EnrichedLead, EnrichmentScore)
- `shared/config.py` - Configuration and ICP criteria
- `integration/enrichment_apis.py` - API clients for Clearbit, Apollo, BuiltWith, etc.
- `processing/scorer.py` - AI scoring engine
- `processing/enricher.py` - Enrichment orchestrator
- `test_enrichment.py` - Test with mock data

## Support

Issues? Questions? Email support or check documentation at docs/lead-enrichment.
