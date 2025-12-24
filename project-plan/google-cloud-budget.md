# Google Cloud Budget Setup with Auto-Shutdown

## Overview

Automated budget monitoring system that:
- ✅ Sends email alerts at **50%** and **70%** usage
- ✅ **Automatically disables** TTS API at **80%** usage
- ✅ Prevents any charges beyond free tier

## Quick Setup (Recommended)

### Option 1: Automated Script

```bash
cd scripts
bash setup-budget.sh
```

This will:
1. Enable required APIs (Billing Budgets, Pub/Sub, Cloud Functions)
2. Create Pub/Sub topic for budget notifications
3. Create budget with $0.01 limit (free tier only)
4. Set up thresholds at 50%, 70%, 80%

### Option 2: Manual Setup via Console

1. Go to [Google Cloud Console - Billing](https://console.cloud.google.com/billing)
2. Select billing account: `My Billing Account 2`
3. Click "Budgets & alerts"
4. Click "CREATE BUDGET"
5. Configure:
   - **Name**: `Lito TTS Free Tier Monitor`
   - **Projects**: `lito-tts-app`
   - **Services**: `Cloud Text-to-Speech API`
   - **Budget amount**: `$0.01`
   - **Thresholds**: 50%, 70%, 80%
   - **Connect Pub/Sub topic**: `budget-alerts`

## Auto-Shutdown Setup (Optional but Recommended)

To enable automatic API shutdown at 80%:

### Deploy as Cloud Function

```bash
cd scripts

# Deploy the monitoring function
gcloud functions deploy budget-monitor \
  --runtime python39 \
  --trigger-topic budget-alerts \
  --entry-point pubsub_handler \
  --source . \
  --project lito-tts-app
```

### Configure Email Alerts

Edit `scripts/budget-monitor.py`:
```python
EMAIL_TO = "anhdhnguyen@gmail.com"
EMAIL_FROM = "your-email@gmail.com"

# Configure SMTP (e.g., Gmail)
# You'll need an app password: https://support.google.com/accounts/answer/185833
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  User makes TTS request                                 │
│  ↓                                                       │
│  Google Cloud TTS API processes                         │
│  ↓                                                       │
│  Usage tracked against budget                           │
│  ↓                                                       │
│  ┌─────────────┬─────────────┬─────────────┐           │
│  │   50%       │    70%      │    80%      │           │
│  │  Email      │   Email     │   Email +   │           │
│  │  Alert      │   Alert     │   SHUTDOWN  │           │
│  └─────────────┴─────────────┴─────────────┘           │
└─────────────────────────────────────────────────────────┘
```

## Budget Thresholds

| Threshold | Action | Details |
|-----------|--------|---------|
| **50%** | 📧 Email Alert | "Courtesy notification - usage at 50%" |
| **70%** | ⚠️ Warning Email | "Approaching limit - API will disable at 80%" |
| **80%** | 🛑 **Auto-Shutdown** | API disabled, email sent with re-enable instructions |

## Free Tier Limits

| Service | Free Tier | With 1,500 char limit |
|---------|-----------|----------------------|
| Standard voices | 4M chars/month | ~2,666 conversions/month |
| WaveNet/Neural | 1M chars/month | ~666 conversions/month |

## Monitoring

### Check Current Usage
```bash
# Via CLI
gcloud billing budgets list --billing-account=013ED6-9913AA-B0942B

# Via Console
https://console.cloud.google.com/billing/budgets?project=lito-tts-app
```

### Check API Status
```bash
gcloud services list --enabled --project=lito-tts-app | grep texttospeech
```

## If API Gets Disabled

The API will automatically disable at 80% usage. To re-enable:

1. **Review usage** to understand what caused the spike:
   ```bash
   gcloud logging read "resource.type=api AND resource.labels.service=texttospeech.googleapis.com" \
     --project=lito-tts-app \
     --limit=100
   ```

2. **Decide on action**:
   - Wait until next month (free tier resets)
   - Increase budget if legitimate usage
   - Investigate if usage seems abnormal

3. **Re-enable API**:
   ```bash
   gcloud services enable texttospeech.googleapis.com --project=lito-tts-app
   ```

## Testing

Test the budget monitor locally:

```bash
cd scripts
python3 budget-monitor.py
```

Test Pub/Sub notification:

```bash
gcloud pubsub topics publish budget-alerts \
  --message='{"costAmount": 0.008, "budgetAmount": 0.01}' \
  --project=lito-tts-app
```

## Security Notes

- Budget alerts use Pub/Sub (secure, encrypted)
- API shutdown requires `serviceusage.services.disable` permission
- Email alerts require SMTP configuration (use app passwords, not main password)

## Cost Protection Summary

| Protection Layer | Status |
|------------------|--------|
| Budget limit set | ✅ $0.01 |
| Email alerts (50%, 70%) | ✅ Configured |
| Auto-shutdown (80%) | ⚠️ Requires Cloud Function deployment |
| Manual monitoring | ✅ Console dashboard |

---

**Recommendation**: Deploy the Cloud Function for complete automation. Without it, you'll get email alerts but need to manually disable the API.
