# Serverless Telegram To-Do Bot

Production-ready serverless Telegram bot powered by AWS Lambda, DynamoDB, and EventBridge.

## Architecture

- **AWS Lambda** - Serverless compute (webhook handler, reminder handler, motivation handler)
- **Amazon DynamoDB** - NoSQL database for tasks, user settings, and motivational messages
- **Amazon API Gateway** - HTTP endpoint for Telegram webhooks
- **Amazon EventBridge Scheduler** - One-time scheduled events for reminders
- **AWS Secrets Manager** - Secure bot token storage
- **AWS SAM** - Infrastructure as Code

## Project Structure

```
telegram-bot-platform/
├── template.yaml              # AWS SAM template
├── lambda/
│   ├── webhook_handler/       # Main Telegram webhook handler
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── handlers/
│   ├── reminder_handler/      # EventBridge-triggered reminder sender
│   │   ├── app.py
│   │   └── requirements.txt
│   └── motivation_handler/    # Daily motivation message sender
│       ├── app.py
│       └── requirements.txt
├── scripts/
│   ├── deploy.sh              # Automated deployment script
│   └── set-webhook.sh         # Set Telegram webhook URL
└── README.md
```

## Prerequisites

- AWS CLI configured with credentials
- AWS SAM CLI installed
- AWS SAM CLI installed
- Python 3.9
- Telegram bot token from @BotFather
- Node.js & NPM (for Mini App)

## Features
- **Smart Task Parsing**: Uses Gemini AI to extract tasks from natural language.
- **Telegram Mini App**: Full React frontend for task management.
- **Gamification**: XP, Levels, and Streaks system.
- **Recurring Reminders**: Powered by EventBridge Scheduler.

## Quick Start

### 1. Store Bot Token

```bash
aws secretsmanager create-secret \
  --name telegram-bot-token \
  --secret-string "YOUR_BOT_TOKEN_HERE" \
  --region us-east-1
```

### 2. Build and Deploy

```bash
# Build Lambda functions
sam build

# Deploy to AWS
sam deploy --guided
```

### 3. Set Telegram Webhook

```bash
# Get webhook URL from SAM outputs
WEBHOOK_URL=$(aws cloudformation describe-stacks \
  --stack-name telegram-bot-platform \
  --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
  --output text)

# Set webhook
./scripts/set-webhook.sh $WEBHOOK_URL
```

## Local Development

Local testing is not applicable for this serverless architecture. Use AWS SAM local invoke for testing:

```bash
# Test webhook handler
sam local invoke WebhookHandlerFunction -e events/test-message.json

# Start local API
sam local start-api
```

## Environment Variables

All environment variables are managed through AWS SAM template:
- `TASKS_TABLE_NAME` - DynamoDB table for tasks
- `USERS_TABLE_NAME` - DynamoDB table for user settings
- `MOTIVATION_TABLE_NAME` - DynamoDB table for motivational messages
- `BOT_TOKEN_SECRET` - Secrets Manager secret name
- `REMINDER_LAMBDA_ARN` - ARN of reminder handler Lambda

## Cost Estimation

- Lambda: ~$1-2/month (within free tier)
- DynamoDB: ~$1/month
- API Gateway: <$1/month (within free tier)
- EventBridge: Minimal ($1 per million schedules)
- **Total: ~$2-5/month**

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## License

MIT
