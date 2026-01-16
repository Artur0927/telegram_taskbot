#!/bin/bash
set -e

echo "🚀 Deploying Serverless Telegram Bot to AWS Lambda..."
echo ""

# Check prerequisites
if ! command -v sam &> /dev/null; then
    echo "❌ Error: AWS SAM CLI not installed"
    echo "Install with: brew install aws-sam-cli"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI not installed"
    echo "Install with: brew install awscli"
    exit 1
fi

# Check if bot token secret exists
BOT_TOKEN_SECRET="telegram-bot-token"
echo "Checking if secret '$BOT_TOKEN_SECRET' exists..."

if ! aws secretsmanager describe-secret --secret-id "$BOT_TOKEN_SECRET" &> /dev/null; then
    echo "⚠️  Secret '$BOT_TOKEN_SECRET' not found!"
    echo ""
    echo "Please create it first:"
    echo "  aws secretsmanager create-secret \\"
    echo "    --name $BOT_TOKEN_SECRET \\"
    echo "    --secret-string \"YOUR_BOT_TOKEN_HERE\""
    echo ""
    read -p "Press Enter to continue if you've created the secret, or Ctrl+C to exit..."
fi

echo "✅ Secret found"
echo ""

# Build
echo "📦 Building Lambda functions..."
sam build

echo ""
echo "🚀 Deploying to AWS..."
echo ""

# Deploy
sam deploy \
  --guided \
  --stack-name telegram-bot-platform \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

echo ""
echo "✅ Deployment complete!"
echo ""

# Get webhook URL
echo "Getting webhook URL..."
WEBHOOK_URL=$(aws cloudformation describe-stacks \
  --stack-name telegram-bot-platform \
  --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
  --output text \
  --region us-east-1)

echo ""
echo "🔗 Webhook URL: $WEBHOOK_URL"
echo ""

# Ask to set webhook
read -p "Do you want to set the Telegram webhook now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Get bot token
    BOT_TOKEN=$(aws secretsmanager get-secret-value \
      --secret-id "$BOT_TOKEN_SECRET" \
      --query SecretString \
      --output text \
      --region us-east-1)
    
    echo "Setting webhook..."
    curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
      -d "url=${WEBHOOK_URL}"
    
    echo ""
    echo "✅ Webhook set successfully!"
fi

echo ""
echo "🎉 Deployment complete! Your bot is now serverless and running on AWS Lambda."
echo ""
echo "Next steps:"
echo "  1. Test your bot by sending /start in Telegram"
echo "  2. Monitor logs: aws logs tail /aws/lambda/telegram-bot-platform-WebhookHandlerFunction --follow"
echo "  3. View DynamoDB tables in AWS Console"
echo ""
