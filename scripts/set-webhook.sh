#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./set-webhook.sh <WEBHOOK_URL>"
    echo ""
    echo "Example:"
    echo "  ./set-webhook.sh https://abc123.execute-api.us-east-1.amazonaws.com/prod/webhook"
    exit 1
fi

WEBHOOK_URL=$1
BOT_TOKEN_SECRET="telegram-bot-token"

echo "🔗 Setting Telegram webhook..."
echo "URL: $WEBHOOK_URL"
echo ""

# Get bot token from Secrets Manager
BOT_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id "$BOT_TOKEN_SECRET" \
  --query SecretString \
  --output text)

# Set webhook
response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=${WEBHOOK_URL}")

echo "Response: $response"

# Check if webhook was set
webhook_info=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")

echo ""
echo "Webhook info:"
echo "$webhook_info" | python3 -m json.tool

echo ""
echo "✅ Webhook configuration complete!"
