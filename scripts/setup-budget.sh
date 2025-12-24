#!/bin/bash
# Setup Google Cloud Budget with Automated Monitoring
# This script sets up budget alerts and Pub/Sub notifications

set -e

PROJECT_ID="lito-tts-app"
BILLING_ACCOUNT="013ED6-9913AA-B0942B"
BUDGET_AMOUNT="0.01"
EMAIL="anhdhnguyen@gmail.com"

echo "🔧 Setting up Google Cloud Budget Monitoring..."
echo "================================================"

# 1. Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable billingbudgets.googleapis.com --project=$PROJECT_ID
gcloud services enable pubsub.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudfunctions.googleapis.com --project=$PROJECT_ID

# 2. Create Pub/Sub topic for budget notifications
echo "📬 Creating Pub/Sub topic..."
TOPIC_NAME="budget-alerts"
gcloud pubsub topics create $TOPIC_NAME --project=$PROJECT_ID || echo "Topic already exists"

# 3. Create budget with Pub/Sub notifications
echo "💰 Creating budget..."
cat > budget-config.json <<EOF
{
  "displayName": "Lito TTS Free Tier Monitor",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"],
    "services": ["services/texttospeech.googleapis.com"]
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "0",
      "nanos": 10000000
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.7,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.8,
      "spendBasis": "CURRENT_SPEND"
    }
  ],
  "notificationsRule": {
    "pubsubTopic": "projects/$PROJECT_ID/topics/$TOPIC_NAME",
    "schemaVersion": "1.0",
    "monitoringNotificationChannels": [],
    "disableDefaultIamRecipients": false
  }
}
EOF

# Create the budget
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="Lito TTS Free Tier Monitor" \
  --budget-amount=$BUDGET_AMOUNT \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=70 \
  --threshold-rule=percent=80 \
  --filter-projects=projects/$PROJECT_ID \
  --filter-services=services/texttospeech.googleapis.com \
  --notifications-rule-pubsub-topic=projects/$PROJECT_ID/topics/$TOPIC_NAME \
  --notifications-rule-monitoring-notification-channels= \
  --notifications-rule-disable-default-iam-recipients=false

echo "✅ Budget created successfully!"

# 4. Set up email notifications (optional - requires Cloud Monitoring)
echo "📧 Setting up email notifications..."
gcloud alpha monitoring channels create \
  --display-name="Lito Budget Alerts" \
  --type=email \
  --channel-labels=email_address=$EMAIL \
  --project=$PROJECT_ID || echo "Email channel setup requires manual configuration"

echo ""
echo "================================================"
echo "✅ Budget Monitoring Setup Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Deploy budget-monitor.py as Cloud Function (optional for auto-shutdown)"
echo "2. Configure email SMTP settings in budget-monitor.py"
echo "3. Test: gcloud pubsub topics publish $TOPIC_NAME --message='test'"
echo ""
echo "Monitor usage at:"
echo "https://console.cloud.google.com/billing/budgets?project=$PROJECT_ID"
echo ""
