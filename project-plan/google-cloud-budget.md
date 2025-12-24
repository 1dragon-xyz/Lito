# Google Cloud Budget Setup

## Objective
Prevent unexpected charges by limiting Google Cloud TTS to the free tier only.

## Steps to Set Budget Alert

### Option 1: Via Google Cloud Console (Recommended)

1. Go to [Google Cloud Console - Billing](https://console.cloud.google.com/billing)
2. Select your billing account: `My Billing Account 2`
3. Click "Budgets & alerts" in the left menu
4. Click "CREATE BUDGET"
5. Configure:
   - **Name**: `Lito TTS - Free Tier Only`
   - **Projects**: Select `lito-tts-app`
   - **Services**: Select `Cloud Text-to-Speech API`
   - **Budget type**: Specified amount
   - **Target amount**: `$0.01` (essentially $0)
   - **Threshold rules**:
     - 50% of budget
     - 90% of budget
     - 100% of budget
   - **Actions**: Email notifications to your email
6. Click "FINISH"

### Option 2: Via gcloud CLI

```bash
# Enable Billing Budget API
gcloud services enable billingbudgets.googleapis.com --project=lito-tts-app

# Create budget
gcloud billing budgets create \
  --billing-account=013ED6-9913AA-B0942B \
  --display-name="Lito TTS Free Tier Only" \
  --budget-amount=0.01 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100 \
  --filter-projects=projects/lito-tts-app \
  --filter-services=services/texttospeech.googleapis.com
```

## Free Tier Limits

| Service | Free Tier | Overage Cost |
|---------|-----------|--------------|
| Standard voices | 4M chars/month | $4 per 1M chars |
| WaveNet/Neural voices | 1M chars/month | $16 per 1M chars |

## Current Usage Estimate

With **1,500 char limit** per conversion:
- Free tier = 4M chars/month
- **~2,666 conversions/month** for free
- **~88 conversions/day**

## Monitoring

Check usage at: [Google Cloud Console - Text-to-Speech](https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics?project=lito-tts-app)

## What Happens if Limit is Reached?

The budget alert will:
1. Send email notifications at 50%, 90%, and 100%
2. **Does NOT automatically stop the service** (Google Cloud doesn't support auto-shutdown)

To truly prevent charges, you would need to:
- Monitor emails closely
- Manually disable the API if approaching limit
- Or set up a Cloud Function to disable the API automatically (advanced)

## Recommendation

For a hobby project, the budget alert is sufficient. You'll get warnings before any charges occur.
