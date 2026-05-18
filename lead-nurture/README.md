# Lead Nurture Agent

AI-powered lead qualification and nurture system that runs on autopilot.

## What It Does

1. **Scores leads 1-10** on AI integration readiness
2. **Auto-generates personalized email sequences** for high-scoring leads (7+)
3. **Surfaces only hot leads (9+)** to you with talking points
4. **References your past work** from Second Brain for credibility

## Quick Test

```bash
cd lead-nurture

# Install dependencies
pip install anthropic pydantic python-dotenv sendgrid httpx

# Copy API key from Second Brain
cat ../second-brain/.env | grep ANTHROPIC_API_KEY > .env

# Run test with 3 example leads
python test_lead_nurture.py
```

This will:
- Score 3 test leads (hot/medium/low)
- Generate email sequences for high-scoring leads
- Save results to `test_lead_nurture_results.json`

## Scoring Criteria

**9-10 (Engage Immediately):**
- Urgent, specific pain costing money now
- Clear budget or authority
- Timeline immediate (weeks)
- Decision maker

**7-8 (Auto-Nurture):**
- Specific operational pain
- Budget signals present
- Timeline within 3 months
- Decision influence

**4-6 (Qualify Further):**
- Clear pain but vague on solution
- Budget/timeline unclear

**1-3 (Deprioritize):**
- "Just exploring"
- No budget signals
- No urgency

## Generated Email Sequences

For leads scoring 7+, automatically generates:

**Email 1** (Immediate):
- Acknowledges specific pain
- Offers quick win
- CTA: Book 15-min audit

**Email 2** (3 days later):
- Shares relevant case study
- Addresses objection
- CTA: Simple question

**Email 3** (5 days after Email 2):
- Final touchpoint
- "Still a priority?" approach
- CTA: Reply or unsubscribe

## Current Status

✅ **Complete:**
- Lead scoring (1-10 scale)
- Multi-dimensional analysis
- Second Brain integration for case studies
- Personalized email generation
- Test harness with 3 lead profiles

⏳ **Todo:**
- Email sending integration (SendGrid)
- Lead intake webhooks
- Email tracking (opens, replies)
- Auto-scheduling for high-intent leads
- CRM integration

## Integration with Second Brain

Automatically:
- Searches for similar client wins
- References relevant case studies in emails
- Uses proven ROI numbers for credibility

## Cost Per Lead

- Scoring: ~$0.01
- Email generation: ~$0.02
- **Total: ~$0.03 per lead**

## Files

- `scoring/lead_scorer.py` - AI scoring (1-10 scale)
- `sequences/email_generator.py` - Personalized email sequences
- `test_lead_nurture.py` - Test with example leads
- `shared/models.py` - Data models

## What's Next

1. **Test current version** - Run `python test_lead_nurture.py`
2. **Review generated emails** - Check if quality/tone is right
3. **Connect email service** - SendGrid or similar for actual sending
4. **Set up intake** - Webhook from website form
5. **Add tracking** - Monitor open rates, reply rates

Target: Auto-nurture 20-30 leads/month → 3-5 become clients
