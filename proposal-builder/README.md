# Unified Proposal Builder

AI-powered proposal generation for AI automation consulting, web development, and combined digital transformation projects.

## What It Does

1. **Generates Proposals** - Creates professional, customized proposals in minutes
2. **Multi-Service** - Handles AI automation, web dev, or combined offerings
3. **Integrates** - Pulls data from Workflow Auditor, Lead Enrichment, Second Brain
4. **Formats** - Exports to Markdown, HTML, JSON (PDF coming soon)
5. **Personalizes** - Every proposal is specific to the client's situation

## Value Proposition

**Time Savings**: 4-6 hours → 20 minutes (95% reduction)

**Typical Use Case**:
- Sales team creating custom proposals
- Currently: Manual writing, copying templates, updating pricing (4-6 hours)
- After: Input discovery notes, generate proposal, review (20 minutes)
- ROI: Immediate

**What Makes This Different**:
- Unified system for multiple service lines
- Pulls from existing analysis (Workflow Auditor, Lead Enrichment)
- AI-generated, not templated
- Consistent quality across team
- Professional formatting included

## Quick Start

### 1. Install Dependencies

```bash
cd proposal-builder
pip install -e .
```

### 2. Set Up Environment

Create `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Test with Mock Data

```bash
python test_proposals.py
```

This will generate 3 sample proposals:
- AI automation consulting
- Web development
- Combined (automation + web)

## Architecture

```
┌──────────────────┐
│  Discovery Call  │ (notes, pain points, goals)
└────────┬─────────┘
         │
         v
┌─────────────────────────┐     ┌──────────────────┐
│  Data Integration       │────▶│ Workflow Auditor │
│  - Workflow analysis    │     │ Lead Enrichment  │
│  - Site analysis        │     │ Second Brain     │
│  - Lead enrichment      │     └──────────────────┘
└────────┬────────────────┘
         │
         v
┌─────────────────────────┐
│  AI Generator           │
│  (Claude)               │
│  - Executive summary    │
│  - Solution design      │
│  - Pricing tiers        │
│  - ROI calculations     │
└────────┬────────────────┘
         │
         v
┌─────────────────────────┐
│  Formatter              │
│  - Markdown             │
│  - HTML                 │
│  - PDF (optional)       │
└─────────────────────────┘
```

## Service Types

### 1. AI Automation

**Inputs:**
- Workflow Auditor analysis
- Pain points and goals
- Current tools and processes

**Output:**
- Custom automation proposal
- 3 implementation tiers
- ROI projections
- Case studies

**Example:**
```python
request = ProposalRequest(
    service_type="ai_automation",
    client=ClientInfo(...),
    discovery=DiscoveryNotes(...),
    automation_inputs=AutomationInputs(
        workflow_analysis=workflow_data,
        workflow_solutions=solutions
    )
)
```

### 2. Web Development

**Inputs:**
- Website analysis (from proposal-agent or manual)
- SEO and performance issues
- Design requirements

**Output:**
- Website rebuild proposal
- Phased implementation
- Tech stack recommendations
- Timeline and pricing

**Example:**
```python
request = ProposalRequest(
    service_type="web_development",
    client=ClientInfo(...),
    discovery=DiscoveryNotes(...),
    webdev_inputs=WebDevInputs(
        site_analysis=analysis,
        seo_issues=[...],
        performance_issues=[...]
    )
)
```

### 3. Combined

**Inputs:**
- Both automation and web dev data
- Integrated requirements

**Output:**
- Comprehensive digital transformation proposal
- Website + automation + integration
- Phased rollout plan
- Higher-tier pricing

## Proposal Structure

Every proposal includes:

1. **Cover**
   - Title (specific to their solution)
   - Client info
   - Date and expiration

2. **Executive Summary**
   - Why this matters now
   - Current state
   - Proposed approach
   - Expected outcomes

3. **Current State Analysis**
   - What they're doing well
   - Current challenges
   - Opportunities for improvement

4. **Proposed Solution**
   - Solution overview
   - Implementation phases (3-5)
   - Deliverables per phase
   - Dependencies and timeline

5. **Pricing (3 Tiers)**
   - Essential/Foundation
   - Recommended/Growth ⭐
   - Comprehensive/Transform
   - Payment terms

6. **ROI Projection**
   - Time saved
   - Cost savings
   - Revenue impact
   - Payback period

7. **Case Studies**
   - 1-2 relevant success stories
   - Similar industry/challenge
   - Specific results

8. **Why Partner With Us**
   - Unique value props
   - Expertise and track record
   - Support and methodology

9. **Next Steps**
   - Concrete actions
   - Timeline to start

10. **Terms**
    - Assumptions
    - Exclusions

## Integration Points

### Workflow Auditor
- Pulls workflow analysis
- Gets solution recommendations
- References ROI calculations

### Lead Enrichment
- Company context
- Industry fit
- Tech stack information
- Decision maker details

### Second Brain
- Relevant case studies
- Similar past projects
- Proven solutions

### proposal-agent (Next.js)
- Can serve as UI frontend
- Calls this system via API
- Handles client-facing interactions

## Pricing Guidelines

Configured in `shared/config.py`:

**AI Automation:**
- Small: $5K-$15K
- Medium: $15K-$35K
- Large: $35K-$75K
- Enterprise: $75K-$200K

**Web Development:**
- Simple: $3K-$8K
- Standard: $8K-$20K
- Advanced: $20K-$50K
- Enterprise: $50K-$150K

**Combined:**
- Starter: $10K-$25K
- Growth: $25K-$60K
- Transform: $60K-$150K
- Enterprise: $150K-$300K

AI uses these as guidance but adjusts based on:
- Scope and complexity
- Timeline requirements
- Client size and budget
- Included services

## Example Output

```markdown
# Smart Client Onboarding System
## Reduce intake time by 68% while improving accuracy

**Prepared for:** Smith & Associates Law Firm
**Contact:** Jennifer Smith (jennifer@smithlaw.com)
**Date:** 2026-04-25

---

## Executive Summary

Your firm is processing 15 new clients per month, with each intake consuming 
2+ hours of staff time — that's 30 hours monthly spent on manual data entry, 
conflict checks, and document generation. At your billing rates, this represents 
$28,000 in annual opportunity cost.

We analyzed your current client onboarding workflow and identified automation 
opportunities that can reduce intake time from 135 minutes to 43 minutes per 
client (68% reduction). This translates to $19,000 in annual savings with a 
4.5-month payback period.

Our proposed solution integrates AI-powered form processing with your existing 
Clio system, automating conflict checks and engagement letter generation while 
maintaining full compliance and attorney oversight.

---

## Investment Options

### Smart Intake & Conflict Check ⭐ RECOMMENDED
**Automate core onboarding while maintaining control**

**Investment:** $12,000 - $18,000
**Timeline:** 4-6 weeks

This tier automates your highest-pain workflows: intelligent form processing, 
automated conflict checking, and engagement letter generation. We integrate 
directly with Clio, so staff continues using familiar systems.

**Included:**
- ✓ AI-powered intake form processing (validates and routes)
- ✓ Automated conflict check against client database
- ✓ Dynamic engagement letter generation
- ✓ Clio integration (bidirectional sync)
- ✓ 2 rounds of revisions based on team feedback
- ✓ Staff training (2 sessions)
- ✓ 30 days post-launch support

**Not Included:**
- ✗ Document assembly for other templates
- ✗ Billing automation

---

## Return on Investment

- **Time Saved:** 10.5 hours/week
- **Annual Cost Savings:** $19,040
- **Payback Period:** 4.5 months
- **3-Year ROI:** 4.2x

---
```

## Customization

### Brand Settings

Edit `shared/config.py`:

```python
DEFAULT_BRAND_NAME = "Your Company"
DEFAULT_TAGLINE = "Your Tagline"
DEFAULT_WEBSITE = "https://yourcompany.com"
```

### Pricing Ranges

Adjust pricing guidance:

```python
PRICING_RANGES = {
    "ai_automation": {
        "small": (5_000, 15_000),
        ...
    }
}
```

### Tone

Set tone in request:

```python
ProposalRequest(
    ...,
    tone="professional"  # or "friendly", "technical"
)
```

## Export Formats

### Markdown

```python
formatter = ProposalFormatter()
markdown = formatter.to_markdown(proposal)
```

Best for: Version control, editing, collaboration

### HTML

```python
html = formatter.to_html(proposal)
```

Best for: Email, web preview, browser printing

### JSON

```python
json_str = formatter.to_json(proposal)
```

Best for: API integration, data storage

### PDF (Coming Soon)

```python
# Requires reportlab or weasyprint
pdf = formatter.to_pdf(proposal)
```

## Next Steps

1. **Test with mock data** ✓
2. **Connect to Workflow Auditor** - Pull real analysis data
3. **Connect to Lead Enrichment** - Auto-populate client context
4. **Connect to Second Brain** - Dynamic case study matching
5. **Add PDF export** - Install reportlab/weasyprint
6. **Build API endpoint** - For proposal-agent frontend
7. **Add e-signature** - DocuSign/PandaDoc integration
8. **Track metrics** - Sent, viewed, accepted rates

## Production Workflow

```python
# 1. After discovery call
discovery_notes = capture_discovery_call()

# 2. Run workflow audit (if automation)
workflow_analysis = await workflow_auditor.analyze(...)

# 3. Get lead enrichment data
lead_data = await lead_enrichment.get_lead(lead_id)

# 4. Generate proposal
request = ProposalRequest(
    service_type="ai_automation",
    client=extract_client_info(lead_data),
    discovery=discovery_notes,
    automation_inputs=AutomationInputs(
        workflow_analysis=workflow_analysis
    )
)

generator = ProposalGenerator(api_key)
proposal = await generator.generate(request)

# 5. Review and send
# (Manual review step before client delivery)

# 6. Export and deliver
formatter = ProposalFormatter()
pdf = formatter.to_pdf(proposal)
send_to_client(pdf, esignature=True)
```

## Files

- `shared/models.py` - Data models for proposals
- `shared/config.py` - Configuration and pricing
- `processing/generator.py` - AI proposal generation
- `processing/formatter.py` - Export formatting
- `integration/system_integrations.py` - Connect to other systems
- `test_proposals.py` - Test with mock data

## Support

Issues? Questions? Email support or check documentation.
