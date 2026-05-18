# SmileCare Dental - Scheduling Automation

**Client**: SmileCare Dental  
**Vertical**: Healthcare  
**Date Completed**: 2024-03-15

## Pain Point

Front desk staff spending 15 hours per week on manual appointment scheduling. Process involved:
- Manual calendar checking (8 min per appointment)
- Phone tag with patients (avg 2-3 attempts)
- Duplicate data entry into Dentrix EHR
- Missed confirmations (~20% of bookings)

This was costing $13,520 annually in staff time and causing patient frustration.

## Solution

Built an AI scheduling assistant that automates 68% of the workflow:

1. **Smart intake form** (Typeform) - Reduced from 18 fields to 3 questions with smart follow-ups
2. **Claude-powered availability** - Checks calendar + provider preferences, suggests 3 optimal slots
3. **Automated confirmations** - SMS/email with personalized messaging
4. **EHR integration** - Daily batch sync to Dentrix

### Architecture

```
Typeform → Make.com → Claude API (Sonnet) → Google Calendar API → Dentrix CSV Import
```

## Tools Used

- Typeform (form builder)
- Make.com (automation platform)
- Claude API (Sonnet 4.6)
- Google Calendar API
- Twilio (SMS)
- Dentrix (EHR system)

## Outcomes

- **68% time reduction** (15hrs/week → 5hrs/week)
- **$9,194 annual savings**
- **Zero double-bookings** since launch
- **+18 point NPS increase** from patients

## Build Details

- **Duration**: 16 hours over 3 weeks
- **Cost to build**: $2,400
- **Monthly tool costs**: $67
- **Payback period**: 3.4 months

## Key Lessons

1. Started with full automation but had to add human-in-loop for edge cases (group appointments, special requests)
2. Claude Haiku was sufficient for intent extraction - saved $200/month vs Sonnet initially
3. Patients loved the personalized confirmation emails - this became a selling point
4. Pattern is highly reusable: used same approach for 2 other dental practices + 1 law firm

## Reusability

**HIGH** - This pattern works for any appointment-based service business:
- Other dental/medical practices
- Law firms (client intake)
- Salons/spas
- Consulting firms

Core pattern: AI-powered availability checking + smart scheduling + automated follow-up
