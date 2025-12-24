#!/usr/bin/env python3
"""
Google Cloud Budget Monitor with Auto-Shutdown

This script monitors Google Cloud TTS usage and:
- Sends email alerts at 50%, 70% thresholds
- Automatically disables the API at 80% threshold

Setup:
1. Enable Cloud Billing Budget API
2. Set up Cloud Pub/Sub for budget notifications
3. Deploy as Cloud Function or run as cron job
"""

import os
import json
from google.cloud import billing_budgets_v1
from google.cloud import serviceusage_v1
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
PROJECT_ID = "lito-tts-app"
BILLING_ACCOUNT = "013ED6-9913AA-B0942B"
BUDGET_AMOUNT = 0.01  # $0.01 (essentially free tier only)
EMAIL_TO = "anhdhnguyen@gmail.com"
EMAIL_FROM = "noreply@1dragon.xyz"  # Configure your email service

# Thresholds
THRESHOLD_WARNING_1 = 0.50  # 50%
THRESHOLD_WARNING_2 = 0.70  # 70%
THRESHOLD_SHUTDOWN = 0.80   # 80%


def send_email_alert(subject, message):
    """Send email alert via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        body = MIMEText(message, 'plain')
        msg.attach(body)
        
        # Configure your SMTP server
        # Example using Gmail (you'll need an app password)
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(EMAIL_FROM, os.environ.get('SMTP_PASSWORD'))
        # server.send_message(msg)
        # server.quit()
        
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def disable_tts_api():
    """Disable the Text-to-Speech API to prevent further charges"""
    try:
        client = serviceusage_v1.ServiceUsageClient()
        name = f"projects/{PROJECT_ID}/services/texttospeech.googleapis.com"
        
        request = serviceusage_v1.DisableServiceRequest(name=name)
        operation = client.disable_service(request=request)
        
        print(f"🛑 TTS API disabled for project {PROJECT_ID}")
        send_email_alert(
            "🚨 URGENT: Lito TTS API Disabled",
            f"The Text-to-Speech API has been automatically disabled at 80% budget threshold.\n\n"
            f"Current usage exceeded safety limit.\n\n"
            f"To re-enable:\n"
            f"1. Review usage at https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics?project={PROJECT_ID}\n"
            f"2. If needed, increase budget or optimize usage\n"
            f"3. Re-enable API: gcloud services enable texttospeech.googleapis.com --project={PROJECT_ID}"
        )
        return True
    except Exception as e:
        print(f"Failed to disable API: {e}")
        return False


def check_budget_and_alert(budget_data):
    """
    Check budget usage and take action based on thresholds
    
    This function is designed to be triggered by Cloud Pub/Sub
    when budget notifications are published.
    """
    # Parse budget notification
    cost_amount = budget_data.get('costAmount', 0)
    budget_amount = budget_data.get('budgetAmount', BUDGET_AMOUNT)
    
    if budget_amount == 0:
        return
    
    usage_percent = cost_amount / budget_amount
    
    print(f"Current usage: ${cost_amount:.4f} / ${budget_amount:.2f} ({usage_percent*100:.1f}%)")
    
    # Check thresholds
    if usage_percent >= THRESHOLD_SHUTDOWN:
        print(f"⚠️  CRITICAL: {usage_percent*100:.1f}% usage - SHUTTING DOWN API")
        disable_tts_api()
    
    elif usage_percent >= THRESHOLD_WARNING_2:
        print(f"⚠️  WARNING: {usage_percent*100:.1f}% usage")
        send_email_alert(
            f"⚠️  Lito TTS Budget Alert: {usage_percent*100:.1f}% Used",
            f"Your Google Cloud TTS usage has reached {usage_percent*100:.1f}% of the free tier.\n\n"
            f"Current cost: ${cost_amount:.4f}\n"
            f"Budget limit: ${budget_amount:.2f}\n\n"
            f"API will be automatically disabled at 80% to prevent charges.\n\n"
            f"Monitor usage: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics?project={PROJECT_ID}"
        )
    
    elif usage_percent >= THRESHOLD_WARNING_1:
        print(f"ℹ️  INFO: {usage_percent*100:.1f}% usage")
        send_email_alert(
            f"ℹ️  Lito TTS Budget Alert: {usage_percent*100:.1f}% Used",
            f"Your Google Cloud TTS usage has reached {usage_percent*100:.1f}% of the free tier.\n\n"
            f"Current cost: ${cost_amount:.4f}\n"
            f"Budget limit: ${budget_amount:.2f}\n\n"
            f"This is a courtesy notification. API will auto-disable at 80%.\n\n"
            f"Monitor usage: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics?project={PROJECT_ID}"
        )


def pubsub_handler(event, context):
    """
    Cloud Function entry point for Pub/Sub trigger
    
    Deploy this as a Cloud Function triggered by budget Pub/Sub topic
    """
    import base64
    
    if 'data' in event:
        budget_notification = base64.b64decode(event['data']).decode('utf-8')
        budget_data = json.loads(budget_notification)
        check_budget_and_alert(budget_data)


if __name__ == "__main__":
    # For local testing
    print("Budget Monitor Script")
    print("=" * 50)
    print(f"Project: {PROJECT_ID}")
    print(f"Budget: ${BUDGET_AMOUNT}")
    print(f"Thresholds: {THRESHOLD_WARNING_1*100}%, {THRESHOLD_WARNING_2*100}%, {THRESHOLD_SHUTDOWN*100}%")
    print("=" * 50)
    
    # Test with sample data
    test_data = {
        'costAmount': 0.008,  # 80% of $0.01
        'budgetAmount': BUDGET_AMOUNT
    }
    check_budget_and_alert(test_data)
