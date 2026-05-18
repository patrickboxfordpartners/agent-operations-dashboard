## Mercury Intelligence

Real-time banking intelligence powered by Mercury's API and Claude AI.

## What It Does

1. **Real-Time Categorization** - Every transaction categorized instantly via webhooks
2. **Smart Spend Analysis** - Detects recurring charges, calculates annual costs
3. **Client Payment Tracking** - Automatically matches incoming payments to clients/invoices
4. **Anomaly Detection** - Flags unusual transactions before they become problems

## Value Proposition

**Time Savings**: 10-15 hours/month → 30 minutes/month (95% reduction)

**Typical Use Case**:
- Small business with 200-300 transactions/month
- Currently: Manual categorization + reconciliation (10-15 hrs/month)
- After: Automatic categorization, review flagged items only (30 min/month)
- ROI: Immediate

**What Makes This Different**:
- Real-time via Mercury webhooks (no Plaid lag)
- Proactive anomaly detection
- Client payment auto-matching
- Subscription cost tracking

## Architecture

```
Mercury Transaction
        ↓
    Webhook fires
        ↓
┌──────────────────┐
│ Webhook Listener │
└────────┬─────────┘
         │
         ↓
┌────────────────────────┐
│  Processing Pipeline   │
├────────────────────────┤
│ 1. Categorize (Claude) │
│ 2. Recurring detection │
│ 3. Anomaly check       │
│ 4. Client match        │
└────────┬───────────────┘
         │
         ↓
┌─────────────────────────┐
│   Actions               │
├─────────────────────────┤
│ • Post to QuickBooks    │
│ • Slack notification    │
│ • Email alert           │
│ • Dashboard update      │
└─────────────────────────┘
```

## Features

### 1. Real-Time Categorization

Every Mercury transaction triggers:
- AI categorization via Claude
- Confidence scoring
- Auto-post if high confidence (>85%)
- Flag for review if low confidence

**Example:**
```
Transaction: $200 from ANTHROPIC*CLAUDE
↓
Category: Software & Subscriptions (95% confidence)
Action: Auto-posted to QuickBooks
```

### 2. Recurring Charge Detection

Automatically identifies subscriptions:
- Pattern analysis (weekly, monthly, quarterly, annual)
- Annual cost calculation
- Alerts on price changes
- Unused subscription detection

**Example:**
```
Detected: Anthropic - $200/month
Annual Cost: $2,400
Last 3 charges: $200.00, $200.00, $200.00
Confidence: 98%
```

### 3. Client Payment Matching

Matches incoming payments:
- AI matches to known clients
- Links to invoices automatically
- Variance detection
- Thank-you email triggers

**Example:**
```
Incoming: $5,000 from ACME CORP
↓
Matched: ACME Corp, Invoice #2024-001
Variance: $0 (exact match)
Actions: 
  ✓ Posted to accounting
  ✓ Email thank-you sent
  ✓ Invoice marked paid
```

### 4. Anomaly Detection

Flags unusual transactions:
- Unusual amount (>2 stddev)
- New/unknown merchant
- Unusual timing (weekends, late night)
- Possible duplicates

**Example:**
```
⚠️ Anomaly Detected
$3,500 to UNKNOWN VENDOR LLC
Reason: First transaction with this vendor
Amount: 3.2x your typical vendor payment
Action: Manual review required
```

## Quick Start

### 1. Install Dependencies

```bash
cd mercury-intelligence
pip install -e .
```

### 2. Set Up Environment

Create `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...
MERCURY_API_KEY=your_mercury_api_key
MERCURY_WEBHOOK_SECRET=your_webhook_secret
MERCURY_ACCOUNT_ID=your_account_id

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
QUICKBOOKS_ENABLED=true
```

### 3. Test with Mock Data

```bash
python test_mercury.py
```

### 4. Set Up Webhook (Production)

```python
# webhook_server.py
from fastapi import FastAPI, Request, HTTPException
from webhooks.listener import WebhookListener
from processing.categorizer import MercuryCategorizer
# ... other imports

app = FastAPI()
listener = WebhookListener()

@app.post("/webhooks/mercury")
async def mercury_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Mercury-Signature", "")
    body = await request.body()
    
    if not listener.verify_signature(body, signature):
        raise HTTPException(status_code=401)
    
    # Parse event
    payload = await request.json()
    event = await listener.handle_webhook(payload)
    
    # Process transaction
    await process_transaction(event.transaction)
    
    return {"status": "ok"}

# Run: uvicorn webhook_server:app --host 0.0.0.0 --port 8000
```

### 5. Configure Mercury Webhook

In Mercury dashboard:
1. Go to Settings → Webhooks
2. Add webhook URL: `https://yourdomain.com/webhooks/mercury`
3. Subscribe to: `transaction.created`, `transaction.updated`
4. Copy webhook secret to `.env`

## Configuration

### Client Names

Add your clients for payment matching:

```python
# In config.py or database
CLIENT_NAMES = [
    "ACME Corp",
    "TechStartup Inc",
    "Smith & Associates"
]
```

### Category Customization

Modify categories in `categorizer.py`:

```python
categories = [
    {"id": "cat_001", "name": "Client Revenue"},
    {"id": "cat_002", "name": "Software & Subscriptions"},
    # ...
]
```

### Anomaly Thresholds

Adjust in `config.py`:

```python
ANOMALY_AMOUNT_THRESHOLD = 2.0  # stddev multiplier
UNUSUAL_TIMING_WINDOW = 22      # flag after 10pm
RECURRING_AMOUNT_TOLERANCE = 0.10  # 10% variance
```

## Integration Points

### QuickBooks/Xero

Auto-post categorized transactions:

```python
if categorized.confidence >= 0.85:
    await quickbooks_client.post_transaction(categorized)
```

### Slack Notifications

Real-time alerts:

```python
if anomaly:
    await slack.post_message(
        channel="#finance",
        text=anomaly_detector.generate_alert_message(anomaly)
    )
```

### Email Alerts

Client payment notifications:

```python
if client_payment:
    await send_email(
        to=team_email,
        subject=f"Payment received from {client_payment.client_name}",
        body=payment_matcher.generate_notification(client_payment)
    )
```

## Example Workflow

**Incoming client payment:**

1. Mercury transaction created
2. Webhook fires → listener receives event
3. Categorizer: "Client Revenue" (98% confidence)
4. Payment matcher: Matches to "ACME Corp", Invoice #2024-001
5. Auto-post to QuickBooks
6. Send Slack notification: "💰 $5,000 received from ACME Corp"
7. Mark invoice as paid
8. Queue thank-you email

**Time: ~2 seconds, zero manual work**

**Suspicious transaction:**

1. Mercury transaction: $3,500 to unknown vendor
2. Webhook fires
3. Anomaly detector: "New merchant + large amount"
4. Send alert: "⚠️ Review required"
5. Team reviews and approves/flags
6. If approved, categorize and post

**Time: 1 minute review, caught before month-end**

## Dashboard Ideas

Build a dashboard showing:

1. **Real-time feed** - Latest transactions with categories
2. **Recurring charges** - All subscriptions with annual costs
3. **Anomalies** - Flagged transactions needing review
4. **Client payments** - Matched vs unmatched
5. **Monthly trends** - Spend by category over time
6. **Alerts** - Price increases, new subscriptions

## Cost Analysis

**Per Month** (300 transactions):
- Mercury: $0 (API is free)
- Claude API: ~$10
- Total: $10/month

**Labor Savings**:
- Before: 15 hrs/month × $50/hr = $750/month
- After: 30 min/month × $50/hr = $25/month
- Savings: $725/month

**ROI**: Immediate (pays for itself on day 1)

## Production Deployment

### Option 1: FastAPI Server

```bash
# webhook_server.py (create this)
uvicorn webhook_server:app --host 0.0.0.0 --port 8000
```

### Option 2: Serverless (AWS Lambda)

Deploy webhook handler as Lambda function behind API Gateway.

### Option 3: Railway/Render

Deploy FastAPI app to Railway or Render (auto-handles HTTPS).

## Security

- Verify webhook signatures (HMAC SHA-256)
- Store API keys in environment variables
- Use HTTPS for webhook endpoint
- Rate limit webhook endpoint
- Log all processing for audit trail

## Files

- `shared/models.py` - Data models
- `shared/config.py` - Configuration
- `webhooks/listener.py` - Webhook handler
- `processing/categorizer.py` - AI categorization
- `analysis/recurring_detector.py` - Subscription detection
- `analysis/anomaly_detector.py` - Anomaly detection
- `analysis/client_payment_matcher.py` - Payment matching
- `test_mercury.py` - Test with mock data

## Next Steps

1. **Test with mock data** ✓
2. **Get Mercury API credentials** - Sign up at mercury.com
3. **Set up webhook endpoint** - Deploy FastAPI server
4. **Configure webhook in Mercury** - Point to your endpoint
5. **Connect to QuickBooks/Xero** - For auto-posting
6. **Set up Slack notifications** - Real-time alerts
7. **Build dashboard** - Monitor all activity
8. **Integrate with Transaction Categorizer** - Unified system

## Support

Mercury API docs: https://docs.mercury.com/
Issues? Questions? Check documentation or email support.
