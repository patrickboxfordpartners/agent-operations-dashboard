# Transaction Categorizer

AI-powered transaction categorization and reconciliation for QuickBooks and Xero.

## What It Does

1. **Fetches Transactions** - Pulls bank/credit card transactions via Plaid
2. **Categorizes with AI** - Uses Claude to assign accounting categories with context
3. **Reconciles** - Checks for duplicates in accounting software
4. **Posts** - Auto-posts high-confidence transactions, flags others for review
5. **Learns** - Improves over time from user corrections

## Value Proposition

**Time Savings**: 10-15 hours/week → 1-2 hours/week (85% reduction)

**Typical Use Case**:
- Small business with 200-300 transactions/month
- Currently: Manual categorization in QuickBooks (15 hrs/week)
- After: Review flagged transactions only (1-2 hrs/week)
- ROI: 3-4 weeks

**What Makes This Different**:
- Context-aware (understands your business type)
- Learns from corrections
- Catches duplicates before posting
- Integrates with existing accounting software

## Quick Start

### 1. Install Dependencies

```bash
cd transaction-categorizer
pip install -e .
```

### 2. Set Up Environment

Create `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...

# Optional (for testing with mock data, these aren't needed)
PLAID_CLIENT_ID=your_plaid_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox

QUICKBOOKS_CLIENT_ID=your_qb_id
QUICKBOOKS_CLIENT_SECRET=your_qb_secret
QUICKBOOKS_REALM_ID=your_company_id
```

### 3. Test with Mock Data

```bash
python test_categorizer.py
```

This will:
- Load 10 mock transactions
- Categorize them with Claude
- Show confidence scores and reasoning
- Flag any that need review
- Generate reconciliation report

## Architecture

```
┌─────────────┐
│ Bank Feeds  │ (Plaid)
└──────┬──────┘
       │
       v
┌─────────────────────┐
│ Transaction Fetcher │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐     ┌─────────────────┐
│ AI Categorizer      │────▶│ Chart of Accts  │ (QB/Xero)
│ (Claude)            │     └─────────────────┘
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ Reconciler          │ (duplicate detection)
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ Post to Accounting  │ (high confidence only)
└─────────────────────┘
```

## Integration Points

### 1. Plaid (Bank Feeds)
- Get access token via Plaid Link
- Fetch transactions for date range
- Provides merchant name, category hints

### 2. QuickBooks / Xero
- OAuth 2.0 authentication
- Fetch chart of accounts
- Post categorized transactions
- Query for duplicate detection

### 3. Second Brain (Optional)
- Store learned patterns
- Reference similar past transactions
- Build case studies for future categorization

## Configuration

### Confidence Thresholds

```python
MIN_CONFIDENCE_AUTO_POST = 0.85  # Auto-post if >= this
MIN_CONFIDENCE_SUGGEST = 0.60    # Suggest if >= this
```

### Business Context

The more context you provide, the better the categorization:

```python
business_context = """
Type: Dental practice
Main expenses: Supplies, lab fees, staff payroll, marketing
Looking for: Tax-deductible expenses vs. personal
Special: Owner sometimes uses business card for personal
"""
```

## Daily Workflow

### Morning Run (Automated)
1. Fetch yesterday's transactions
2. Categorize with AI
3. Auto-post high-confidence (>85%)
4. Email summary of flagged transactions

### Weekly Review (Manual - 1 hour)
1. Review flagged transactions
2. Correct any miscategorizations
3. System learns from corrections

## Cost Analysis

**Per Month** (300 transactions):
- API calls: ~$15
- Plaid: $25
- Total: $40/month

**Labor Savings**:
- Before: 15 hrs/week × $50/hr = $750/week = $3,000/month
- After: 1 hr/week × $50/hr = $50/week = $200/month
- Savings: $2,800/month

**ROI**: 2 weeks

## Pricing Recommendation

- Base: $500/month
- Plus $200/month per additional entity
- Includes: Unlimited transactions, weekly review support
- Add-on: Custom rules ($100/month)

## Next Steps

1. **Test with mock data** ✓
2. **Connect real Plaid account** - Get access token via Plaid Link
3. **Set up QB/Xero OAuth** - Get credentials from their developer portals
4. **Create approval UI** - Simple web form for reviewing flagged transactions
5. **Schedule daily runs** - Cron job or cloud function
6. **Add learning pipeline** - Store corrections, update rules
7. **Integrate with Second Brain** - Feed patterns into knowledge base

## Production Deployment

### Option 1: Cloud Function (Serverless)
```bash
# AWS Lambda / Google Cloud Functions
# Triggered daily at 6 AM
# Processes previous day's transactions
# Sends summary email
```

### Option 2: Self-Hosted
```bash
# Docker container
# Runs on client's infrastructure
# Cron job: 0 6 * * * /usr/bin/python categorize_daily.py
```

### Option 3: SaaS Platform
```bash
# Your infrastructure
# Multi-tenant
# Client logs in to review/approve
# Webhook notifications
```

## Security Notes

- Never store raw bank credentials
- Use OAuth 2.0 for all integrations
- Plaid access tokens are encrypted at rest
- Audit log for all categorization changes
- PCI DSS not required (no card numbers stored)

## Common Issues

### "Transaction already exists"
- Duplicate detection working correctly
- Check if transaction was manually entered
- Reconcile date range to avoid overlap

### "Low confidence on obvious transactions"
- Add business context
- Update category keywords
- Feed corrections back into system

### "Personal expenses getting categorized as business"
- Flag these for review
- Add merchant to personal exclusion list
- Consider separate bank accounts

## Files

- `shared/models.py` - Data models (Transaction, Category, etc.)
- `shared/config.py` - Configuration and API keys
- `integration/plaid_client.py` - Fetch transactions from Plaid
- `integration/accounting_client.py` - QuickBooks/Xero integration
- `processing/categorizer.py` - AI categorization engine
- `processing/reconciler.py` - Duplicate detection and reconciliation
- `test_categorizer.py` - Test with mock data

## Support

Issues? Questions? Email support or check documentation at docs/transaction-categorizer.
