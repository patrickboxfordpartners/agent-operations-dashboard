# Workflow Auditor

Converts client workflow descriptions into AI automation roadmaps with ROI calculations.

## Status

🔄 **In Progress** - Core engine built, needs Notion integration

## What It Does

1. **Input:** Text description, Loom video transcript, or Google Doc
2. **Processing:**
   - Extracts structured workflow (steps, pain points, costs)
   - Searches Second Brain for similar solved problems
   - Generates 3 automation solutions (conservative/balanced/aggressive)
3. **Output:** Client-ready audit with ROI calculations

## Quick Test

```bash
cd workflow-auditor

# Install dependencies
pip install -e .

# Copy environment config
cp .env.example .env
# Add your ANTHROPIC_API_KEY (same as Second Brain)

# Run test audit
python test_auditor.py
```

This will:
- Process an example accounting firm workflow
- Generate 3 automation solutions
- Save results to `test_audit_output.json`

## Current Status

✅ **Complete:**
- Workflow extraction (Claude)
- Solution generation (Claude Opus)
- Second Brain integration for similar solutions
- Cost/ROI calculations
- Test harness

🔄 **In Progress:**
- Notion output formatter
- Web intake form

⏳ **Todo:**
- Make.com webhooks for Loom/Doc intake
- Email notification on audit complete
- Win/loss tracking

## Next Steps

### 1. Test Current Version

```bash
python test_auditor.py
```

Review `test_audit_output.json` to see the generated audit.

### 2. Set Up Notion (Optional)

If you want Notion output:

1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy token to `.env` as `NOTION_TOKEN`
4. Create a database for audits
5. Share database with your integration
6. Add database ID to `.env`

### 3. Add Real Projects to Second Brain

The auditor gets better when Second Brain has more projects to reference:

```bash
cd ../second-brain
# Add 3-5 real past projects
```

## Architecture

```
Client Input → Workflow Extractor (Claude Sonnet)
                      ↓
             Second Brain Search (similar solutions)
                      ↓
             Solution Generator (Claude Opus)
                      ↓
             Output Formatter (Notion/JSON)
```

## Cost Per Audit

- Workflow extraction: ~$0.01
- Solution generation: ~$0.15 (Opus)
- Second Brain search: ~$0.01
- **Total: ~$0.17 per audit**

## Revenue Model

**Option A: Free audit → paid implementation**
- Audit: Free
- Implementation: $1,200-$6,500
- Target close rate: 35%

**Option B: Paid audit**
- Audit: $497
- Credited if they proceed
- Higher qualification

## Files

- `processing/workflow_extractor.py` - Extracts structured workflow
- `processing/solution_generator.py` - Generates 3 solutions
- `processing/auditor.py` - Main orchestrator
- `test_auditor.py` - Test with example data
- `shared/models.py` - Pydantic data models
- `shared/config.py` - Configuration

## Integration with Second Brain

The auditor automatically:
1. Searches Second Brain for similar projects
2. References proven solutions in generated audits
3. Uses actual ROI data from past work

When Second Brain is empty, audits still work but won't have proof points.

## What's Next?

Once you're happy with the audit quality:
1. Build Notion output formatter (pretty client-facing page)
2. Set up intake form (Typeform + webhook)
3. Test with 3-5 real prospects
4. Iterate based on feedback
5. Scale outreach

Target: 20 audits/month → 7 clients closed → $15k MRR
