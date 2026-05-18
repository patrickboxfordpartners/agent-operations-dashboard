# Micro-Workflow Auditor
## Technical Architecture v1.0

---

## System Overview

Converts unstructured process descriptions (Looms, Google Docs, emails) into AI integration roadmaps. Outputs: current state map, bottlenecks, 3 re-engineered solutions with tools, prompts, and ROI estimates.

**Key differentiator:** This IS your consulting deliverable. You're productizing your audit methodology.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      INTAKE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Email Webhook       Form Submission      Manual Upload          │
│  (Gmail/Outlook) →   (Typeform/Tally) →   (Notion button)       │
│         ↓                   ↓                    ↓               │
│                    Webhook Handler (Make/Zapier)                 │
│                            ↓                                      │
│                    Content Normalizer                            │
│  - Extract: video URL, doc link, raw text                       │
│  - Metadata: client name, vertical, urgency                      │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: Transcribe (if video)                                  │
│  - Loom → transcript via Loom API                                │
│  - Other video → Whisper API                                     │
│                            ↓                                      │
│  Step 2: Structure Extraction (Claude Opus 4.7)                 │
│  System prompt: "You are a process mining expert..."            │
│  Output: JSON workflow schema                                    │
│                            ↓                                      │
│  Step 3: Bottleneck Analysis (Claude Sonnet 4.6)               │
│  - Identify: manual steps, wait times, error-prone points       │
│  - Calculate: time cost per step, failure rates                  │
│                            ↓                                      │
│  Step 4: Solution Generation (Claude Opus 4.7 + Second Brain)  │
│  - Query Second Brain for similar solved problems               │
│  - Generate 3 solutions: Conservative / Balanced / Aggressive    │
│  - Each includes: architecture, tools, prompts, cost, timeline  │
│                            ↓                                      │
│  Step 5: ROI Calculation                                         │
│  - Time saved × hourly rate × frequency                          │
│  - Build cost (your hours × rate + tool costs)                  │
│  - Payback period, 12-month ROI                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Notion Page (Client View)         Internal Dashboard            │
│  - Current process map              - All audits, sortable       │
│  - Bottlenecks highlighted          - ROI distribution           │
│  - 3 solution options               - Win rate tracking          │
│  - ROI comparison table             - Proposal → Close time      │
│  - Next steps CTA                                                │
│                            ↓                                      │
│               Optional: Auto-send summary email                  │
│               (if ROI ≥ 3x and client opted in)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Tool | Cost | Why |
|-----------|------|------|-----|
| **Webhook receiver** | Make.com | $9/mo (Core plan) | Visual builder, no code, 10k ops/month |
| **Transcription** | Loom API (free) + Whisper ($0.006/min) | ~$5/mo | Loom API for Looms, Whisper for everything else |
| **LLM** | Claude Opus 4.7 (strategy) + Sonnet 4.6 (execution) | ~$50/mo | Opus for complex reasoning, Sonnet for speed |
| **Database** | Notion API | Free | Client-facing + internal CRM |
| **File storage** | S3 | $1/mo | Store transcripts, PDFs, recordings |
| **Prompt caching** | Built into Claude API | -60% cost | Reuse system prompts across audits |
| **Monitoring** | Langfuse | Free tier | Track audit quality, token usage |

**Total:** ~$65/month for 30-50 audits

---

## Data Flow & Schemas

### Input Schema (Normalized)

```json
{
  "audit_id": "aud_2024_04_dental_scheduling",
  "received_at": "2024-04-25T10:30:00Z",
  "source": "typeform_submission",
  "client": {
    "name": "SmileCare Dental",
    "email": "admin@smilecare.com",
    "vertical": "healthcare",
    "company_size": "5-10",
    "urgency": "medium"
  },
  "input": {
    "type": "loom_video",
    "url": "https://loom.com/share/abc123",
    "description": "How we currently handle new patient scheduling",
    "duration_seconds": 312
  }
}
```

### Workflow Schema (After Step 2)

```json
{
  "workflow_name": "New Patient Scheduling",
  "frequency": "20-30 times per week",
  "total_time_per_cycle": "25 minutes",
  "people_involved": ["Front desk staff", "Office manager"],
  "steps": [
    {
      "step_number": 1,
      "action": "Patient calls or submits web form",
      "performed_by": "Patient",
      "tool": "Phone or website",
      "avg_duration_minutes": 3,
      "pain_points": ["Form has 18 fields, high abandonment"],
      "automation_potential": "high"
    },
    {
      "step_number": 2,
      "action": "Front desk manually checks calendar",
      "performed_by": "Front desk staff",
      "tool": "Google Calendar + paper notes",
      "avg_duration_minutes": 8,
      "pain_points": [
        "Double-bookings happen monthly",
        "No visibility into provider preferences",
        "Interrupts other work"
      ],
      "automation_potential": "very_high"
    },
    {
      "step_number": 3,
      "action": "Call patient back with options",
      "performed_by": "Front desk staff",
      "tool": "Phone",
      "avg_duration_minutes": 7,
      "pain_points": ["Phone tag, takes 2-3 attempts avg"],
      "automation_potential": "medium"
    },
    {
      "step_number": 4,
      "action": "Manually enter into EHR system",
      "performed_by": "Front desk staff",
      "tool": "Dentrix",
      "avg_duration_minutes": 5,
      "pain_points": ["Duplicate data entry from calendar"],
      "automation_potential": "high"
    },
    {
      "step_number": 5,
      "action": "Send confirmation email",
      "performed_by": "Front desk staff",
      "tool": "Gmail (manual)",
      "avg_duration_minutes": 2,
      "pain_points": ["Inconsistent messaging", "Forgotten ~20% of time"],
      "automation_potential": "very_high"
    }
  ],
  "current_cost": {
    "time_per_week_hours": 10.4,
    "hourly_rate": 25,
    "weekly_cost": 260,
    "annual_cost": 13520
  }
}
```

### Solution Schema (After Step 4)

```json
{
  "solution_1_conservative": {
    "name": "Smart Form + Auto-Response",
    "description": "Reduce form friction and automate confirmation emails",
    "automation_level": 0.30,
    "changes": [
      {
        "step": 1,
        "change": "Replace 18-field form with conversational AI form (3 questions + smart follow-ups)"
      },
      {
        "step": 5,
        "change": "Auto-send confirmation email via Make + Claude template generation"
      }
    ],
    "architecture": {
      "diagram": "Web form → Make webhook → Claude (extract + validate) → Email API",
      "tools": ["Typeform", "Make.com", "Claude API (Haiku)", "SendGrid"],
      "integration_points": ["Typeform webhook", "Gmail/SendGrid SMTP"]
    },
    "prompts": {
      "validation_prompt": "Extract: patient name, preferred dates (3 options), service type, insurance. Flag if missing critical info.",
      "email_prompt": "Generate warm, professional confirmation email. Include: appointment details, what to bring, parking info. Match tone of this example: [...]"
    },
    "estimated_outcomes": {
      "time_saved_per_cycle_minutes": 7,
      "new_cycle_time_minutes": 18,
      "time_savings_percent": 0.28,
      "annual_cost_after": 9734,
      "annual_savings": 3786
    },
    "build_cost": {
      "your_hours": 8,
      "your_rate": 150,
      "your_cost": 1200,
      "tool_setup": 100,
      "total": 1300,
      "payback_months": 4.1
    },
    "monthly_tool_cost": 38,
    "risks": ["Low adoption if staff prefers phone", "Form completion rate must be monitored"],
    "timeline_weeks": 2
  },
  "solution_2_balanced": {
    "name": "AI Scheduling Assistant",
    "description": "Full calendar automation with human-in-loop for edge cases",
    "automation_level": 0.68,
    "changes": [
      {
        "step": 1,
        "change": "Conversational AI form with instant availability shown"
      },
      {
        "step": 2,
        "change": "Claude queries calendar, checks provider preferences, suggests 3 slots"
      },
      {
        "step": 3,
        "change": "Automated SMS/email with options, patient confirms via link"
      },
      {
        "step": 4,
        "change": "Auto-sync to EHR via Dentrix API (if available) or daily batch import"
      },
      {
        "step": 5,
        "change": "Automated confirmation + pre-appointment reminders"
      }
    ],
    "architecture": {
      "diagram": "Form → Make → Claude (availability check + preference matching) → Calendar API → EHR sync → Email/SMS",
      "tools": ["Typeform", "Make.com", "Claude API (Sonnet)", "Google Calendar API", "Twilio", "Dentrix API or CSV import"],
      "integration_points": ["Google Calendar API", "Dentrix API (if available)", "Twilio SMS API"]
    },
    "prompts": {
      "scheduling_prompt": "Given patient request and current calendar, find 3 optimal slots considering: provider availability, appointment type duration, patient history. Flag: double-book risks, unusual requests.",
      "confirmation_prompt": "Generate confirmation message with: appointment time, provider name, service, location, what to bring, parking. Add: 48hr cancellation policy reminder."
    },
    "estimated_outcomes": {
      "time_saved_per_cycle_minutes": 17,
      "new_cycle_time_minutes": 8,
      "time_savings_percent": 0.68,
      "annual_cost_after": 4326,
      "annual_savings": 9194
    },
    "build_cost": {
      "your_hours": 16,
      "your_rate": 150,
      "your_cost": 2400,
      "tool_setup": 200,
      "total": 2600,
      "payback_months": 3.4
    },
    "monthly_tool_cost": 67,
    "risks": ["EHR integration may require IT support", "Edge cases (group appointments, special requests) need review queue"],
    "timeline_weeks": 3,
    "proven_similar": "Yes - same pattern used for law firm intake (3 implementations, avg 65% savings)"
  },
  "solution_3_aggressive": {
    "name": "Autonomous Scheduling Engine",
    "description": "Zero-touch scheduling with ML-powered conflict resolution",
    "automation_level": 0.92,
    "changes": "Full replacement of steps 1-5 with AI-native scheduling system",
    "architecture": {
      "diagram": "Multi-channel intake (web/SMS/voice) → Claude Opus (decision engine) → Calendar + EHR → Automated follow-up sequences",
      "tools": ["Custom React form", "Retool for admin", "Make.com", "Claude API (Opus)", "Twilio Voice + SMS", "Dentrix API", "Segment for analytics"],
      "integration_points": ["Full EHR integration", "Voice AI (Twilio Autopilot)", "Payment pre-collection"]
    },
    "estimated_outcomes": {
      "time_saved_per_cycle_minutes": 23,
      "new_cycle_time_minutes": 2,
      "time_savings_percent": 0.92,
      "annual_cost_after": 1081,
      "annual_savings": 12439
    },
    "build_cost": {
      "your_hours": 40,
      "your_rate": 150,
      "your_cost": 6000,
      "tool_setup": 500,
      "total": 6500,
      "payback_months": 6.3
    },
    "monthly_tool_cost": 157,
    "risks": ["High build complexity", "May feel impersonal to patients", "Requires change management"],
    "timeline_weeks": 8,
    "recommendation": "Only if scaling to multiple locations"
  },
  "recommended_solution": "solution_2_balanced",
  "recommendation_reasoning": "Best ROI/effort ratio. 3.4mo payback, proven pattern with existing case studies. Aggressive option has diminishing returns for single-location practice."
}
```

### Output (Notion Page)

**Page title:** `[AUDIT] SmileCare Dental - Scheduling Automation`

**Properties:**
- Status: Delivered
- Client: SmileCare Dental
- Vertical: Healthcare
- Received: 2024-04-25
- ROI (Balanced): 3.5x
- Recommended Solution: Balanced
- Urgency: Medium

**Page content:** (Markdown)
```markdown
# Scheduling Process Audit
**For:** SmileCare Dental  
**Date:** April 25, 2024  
**Current Annual Cost:** $13,520 in staff time

---

## Current State

You're spending **10.4 hours per week** on scheduling tasks. Here's the breakdown:

[Workflow diagram - use Mermaid or Excalidraw]

### Biggest Bottlenecks:
1. ⏱️ **Step 2: Manual calendar checking (8min/appointment)** - Double-bookings, no provider preference logic
2. 📞 **Step 3: Phone tag (7min/appointment)** - Takes 2-3 attempts on average
3. 💾 **Step 4: Duplicate data entry (5min/appointment)** - Re-typing from calendar into Dentrix

---

## 3 Solutions (Pick Your Automation Level)

| Solution | Time Savings | Annual Savings | Build Cost | Payback | Our Recommendation |
|----------|--------------|----------------|------------|---------|-------------------|
| **Conservative** | 28% | $3,786 | $1,300 | 4.1mo | ⭐ Start here if new to automation |
| **Balanced** | 68% | $9,194 | $2,600 | 3.4mo | ⭐⭐⭐ **Best ROI** |
| **Aggressive** | 92% | $12,439 | $6,500 | 6.3mo | Only if multi-location |

---

## ⭐ Recommended: Balanced Solution
### AI Scheduling Assistant

**What changes:**
- Patients get instant availability on your web form (no back-and-forth)
- Claude checks your calendar + provider preferences automatically
- Confirmation emails/SMS sent instantly
- Daily sync to Dentrix (no more re-typing)

**What stays the same:**
- You review edge cases (group appointments, special requests)
- Phone option still available for patients who prefer it

**Proof it works:**
We've built this exact pattern for 3 other healthcare clients. Average result: **65% time savings**, payback in ~3 months.

### Architecture
```
Web form → Make.com → Claude (availability check) → Google Calendar → Dentrix → Confirmation
```

**Tools used:**
- Typeform (smart form)
- Make.com (connects everything)
- Claude API (the "brain")
- Twilio (SMS confirmations)

**Timeline:** 3 weeks from kickoff to launch

**Monthly cost after build:** $67 for tools

---

## ROI Breakdown (Balanced Solution)

| Metric | Current | After Automation | Improvement |
|--------|---------|------------------|-------------|
| Time per appointment | 25min | 8min | -17min (68%) |
| Weekly hours | 10.4hrs | 3.3hrs | -7.1hrs |
| Annual cost | $13,520 | $4,326 | **-$9,194** |

**Build investment:** $2,600  
**Payback period:** 3.4 months  
**12-month ROI:** 3.5x

---

## Next Steps

**Option 1:** Schedule a 30-min call to walk through the recommended solution  
[Book a call](calendar-link)

**Option 2:** Start with the conservative solution first  
[Accept proposal](typeform-link)

**Questions?** Reply to this page (we get notified) or email [your-email]

---

*Audit completed by [Your Company] on April 25, 2024*  
*Based on: 7min Loom walkthrough of current process*
```

---

## Implementation Guide

### Phase 1: MVP (Week 1)

**Day 1: Setup infrastructure**

```bash
# Create Make.com account (free trial)
# Create scenarios:

Scenario 1: "Intake Handler"
Trigger: Webhook (generate URL)
Modules:
  1. Webhook catch
  2. Router (by input type: loom/doc/text)
     - Branch A: Loom → HTTP request to Loom API → get transcript
     - Branch B: Google Doc → Google Docs module → get text
     - Branch C: Raw text → pass through
  3. Text aggregator
  4. HTTP request to your processing endpoint

Scenario 2: "Audit Generator"  
Trigger: HTTP request from your app
Modules:
  1. Receive normalized input
  2. HTTP to your FastAPI endpoint
  3. Wait for completion
  4. Create Notion page with results
  5. Send email notification
```

**Day 2-3: Build processing engine**

File: `auditor/main.py`
```python
from fastapi import FastAPI, BackgroundTasks
from anthropic import Anthropic
import json

app = FastAPI()
claude = Anthropic()

SYSTEM_PROMPT = """You are an expert process mining consultant specializing in AI automation opportunities.

When given a workflow description, you must:
1. Extract a structured step-by-step process (JSON format)
2. Identify bottlenecks and pain points
3. Calculate time/cost implications
4. Generate 3 solutions with different automation levels

Be specific: name exact tools, provide prompt templates, estimate hours accurately.
Base recommendations on proven patterns, not theoretical possibilities."""

@app.post("/audit")
async def create_audit(input: AuditInput, background_tasks: BackgroundTasks):
    audit_id = generate_id()
    
    # Run in background so Make doesn't timeout
    background_tasks.add_task(process_audit, audit_id, input)
    
    return {"audit_id": audit_id, "status": "processing"}

async def process_audit(audit_id: str, input: AuditInput):
    # Step 1: Transcribe if needed
    if input.type == "loom_video":
        transcript = await get_loom_transcript(input.url)
    else:
        transcript = input.text
    
    # Step 2: Extract workflow structure
    workflow = await extract_workflow(transcript, input.client)
    
    # Step 3: Query second brain for similar solutions
    similar_solutions = await brain.search(
        query=workflow['workflow_name'],
        vertical=input.client.vertical,
        limit=3
    )
    
    # Step 4: Generate solutions
    solutions = await generate_solutions(
        workflow=workflow,
        similar_solutions=similar_solutions,
        client=input.client
    )
    
    # Step 5: Create output
    await create_notion_page(audit_id, workflow, solutions)
    await send_notification(input.client.email, audit_id)

async def extract_workflow(transcript: str, client: Client) -> dict:
    """Use Claude to structure the workflow"""
    
    prompt = f"""Analyze this workflow description and extract a structured process.

Client context:
- Vertical: {client.vertical}
- Company size: {client.company_size}
- Urgency: {client.urgency}

Workflow description:
{transcript}

Return JSON matching this schema:
{{
  "workflow_name": "...",
  "frequency": "... per week/month",
  "steps": [
    {{
      "step_number": 1,
      "action": "...",
      "performed_by": "...",
      "tool": "...",
      "avg_duration_minutes": X,
      "pain_points": ["..."],
      "automation_potential": "low/medium/high/very_high"
    }}
  ],
  "current_cost": {{
    "time_per_week_hours": X,
    "hourly_rate": X (estimate based on role),
    "annual_cost": X
  }}
}}
"""
    
    message = await claude.messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(message.content[0].text)

async def generate_solutions(workflow: dict, similar_solutions: list, client: Client) -> dict:
    """Generate 3 automation solutions"""
    
    context = f"""Similar solutions we've built before:
{json.dumps(similar_solutions, indent=2)}

Use these as proof points and architectural inspiration."""
    
    prompt = f"""Given this workflow, design 3 AI automation solutions:

Current workflow:
{json.dumps(workflow, indent=2)}

{context}

Generate 3 solutions:
1. **Conservative** (30-40% automation): Quick wins, minimal risk
2. **Balanced** (60-75% automation): Best ROI/effort ratio
3. **Aggressive** (85-95% automation): Maximum automation, higher complexity

For each solution provide:
- Exact architecture diagram (text-based)
- Specific tools (real products, no vaporware)
- Prompt templates for Claude
- ROI calculation (time saved × hourly rate - build cost)
- Build timeline in weeks
- Monthly tool costs
- Risks and mitigation

Return JSON matching the schema from the architecture doc."""
    
    message = await claude.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        metadata={"audit_id": workflow.get('audit_id')}
    )
    
    return json.loads(message.content[0].text)
```

**Day 4-5: Build Notion integration**

```python
from notion_client import Client as NotionClient

notion = NotionClient(auth=os.environ["NOTION_TOKEN"])

async def create_notion_page(audit_id: str, workflow: dict, solutions: dict):
    """Create client-facing audit page"""
    
    # Use Notion blocks API to build the page structure
    # See full template in architecture doc above
    
    page = await notion.pages.create(
        parent={"database_id": AUDITS_DATABASE_ID},
        properties={
            "Title": f"[AUDIT] {workflow['client_name']} - {workflow['workflow_name']}",
            "Status": "Delivered",
            "Client": workflow['client_name'],
            "Vertical": workflow['vertical'],
            "ROI (Balanced)": solutions['solution_2_balanced']['build_cost']['payback_months'],
            "Recommended": solutions['recommended_solution']
        },
        children=build_page_blocks(workflow, solutions)
    )
    
    return page['url']
```

### Phase 2: Proactive Mode (Week 2)

**Monitor job postings for automation opportunities**

```python
# New scenario in Make:
Scenario: "Job Posting Monitor"
Trigger: RSS feed (Indeed, LinkedIn, AngelList - search for "hiring [operations/admin/scheduling]")
Schedule: Every 4 hours
Modules:
  1. RSS feed aggregator
  2. Filter: only job posts that mention manual processes
  3. HTTP to your auditor endpoint
  4. Create lead in CRM with "Auto-generated audit" tag
```

**Auto-generate audits from job descriptions**

```python
@app.post("/audit/from-job-posting")
async def audit_from_job(job_posting: JobPosting):
    """Reverse-engineer workflow from job description"""
    
    prompt = f"""This company is hiring for: {job_posting.title}

Job description:
{job_posting.description}

Based on the responsibilities listed, reconstruct:
1. The manual workflow they're trying to staff
2. Pain points (why they're hiring)
3. An AI automation solution that could eliminate 60%+ of the role

This is for outbound prospecting - be compelling but honest."""
    
    # Rest of processing...
    # Output: Audit + cold outreach email draft
```

### Phase 3: Integration with Second Brain (Week 3)

**Feed completed audits → client wins → Second Brain**

```python
@app.post("/audit/complete")
async def mark_audit_complete(audit_id: str, outcome: AuditOutcome):
    """When client accepts a solution, feed it to Second Brain"""
    
    if outcome.status == "accepted":
        # This becomes a project in your Second Brain
        await brain.ingest_project({
            "client": outcome.client_name,
            "vertical": outcome.vertical,
            "pain_point": outcome.original_workflow['workflow_name'],
            "solution": outcome.accepted_solution,
            "roi_metric": f"{outcome.time_savings_percent}% time reduction",
            "tools_used": outcome.accepted_solution['tools'],
            "proof_point": True  # Now you can reference this in future audits
        })
```

---

## Pricing Model

### Option A: Free audit, paid implementation
- Audit is free (takes you 15min to review the output)
- Charge for implementation: $2,400 (balanced) or $1,200 (conservative)
- **Close rate:** Typically 30-40% (audits are valuable, builds trust)

### Option B: Paid audit ($497), credited toward implementation
- Charge $497 for audit
- Credit toward implementation if they proceed
- **Close rate:** Typically 50-60% (self-qualifies buyers)

### Option C: Freemium SaaS
- Free tier: 1 audit per month
- Pro tier ($99/mo): Unlimited audits + solution templates
- Enterprise ($499/mo): White-label for agencies

**Recommendation for you:** Start with Option A. Use the auditor to generate leads, close implementation deals.

---

## Success Metrics

Track these in your Notion dashboard:

1. **Audits delivered:** Count
2. **Avg time to generate:** Should be <30min of your time
3. **Proposals sent:** Count of audits that convert to proposals
4. **Close rate:** Proposals → signed contracts
5. **Avg deal size:** Revenue per closed audit
6. **Time to close:** Days from audit → contract signed

**Target KPIs (Month 3):**
- 20 audits delivered/month
- 15min avg time investment per audit
- 35% close rate
- $2,200 avg deal size
- **Result: $15,400 MRR from 7 closed deals**

---

## Next Steps

**Week 1:**
1. Set up Make.com scenarios (use templates above)
2. Build FastAPI processing engine
3. Create Notion database + page template
4. Test with 2-3 past client scenarios

**Week 2:**
5. Launch intake form on your website
6. Email 10 past prospects with "Free workflow audit" offer
7. Monitor and refine Claude prompts based on output quality

**Week 3:**
8. Add job posting monitor (proactive mode)
9. Integrate with Second Brain for solution recommendations
10. Track first 5 audits → proposals → closes

---

Ready to build? Start with the Second Brain this week, Workflow Auditor next week. The Second Brain makes the Auditor's outputs 10x better because it references your real case studies.
