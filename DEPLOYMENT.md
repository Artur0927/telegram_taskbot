# Deployment Guide - Serverless Telegram Bot

Complete guide for deploying the Telegram To-Do bot to AWS Lambda.

## Prerequisites

### 1. Install Tools

```bash
# AWS CLI
brew install awscli

# AWS SAM CLI
brew install aws-sam-cli

# Configure AWS credentials
aws configure
```

### 2. Get Telegram Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Deployment Steps

### Step 1: Store Bot Token in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name telegram-bot-token \
  --secret-string "YOUR_BOT_TOKEN_HERE" \
  --region us-east-1
```

### Step 2: Deploy Infrastructure

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run deployment
./scripts/deploy.sh
```

The script will:
1. Validate prerequisites
2. Build Lambda functions with dependencies
3. Deploy SAM stack to AWS
4. Create DynamoDB tables
5. Set up API Gateway
6. Configure IAM roles
7. Optionally set Telegram webhook

### Step 3: Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name telegram-bot-platform \
  --region us-east-1

# Get webhook URL
aws cloudformation describe-stacks \
  --stack-name telegram-bot-platform \
  --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
  --output text \
  --region us-east-1
```

### Step 4: Set Webhook (if not done during deployment)

```bash
# Get webhook URL from outputs
WEBHOOK_URL=$(aws cloudformation describe-stacks \
  --stack-name telegram-bot-platform \
  --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
  --output text \
  --region us-east-1)

# Set webhook
./scripts/set-webhook.sh $WEBHOOK_URL
```

## Testing

### Test in Telegram

1. Open Telegram
2. Search for your bot by username
3. Send `/start` - you should get a welcome message
4. Try creating a task: `"Buy milk tomorrow at 18:00"`
5. List tasks: `/tasks`

### Monitor Logs

```bash
# Watch webhook handler logs
aws logs tail /aws/lambda/telegram-bot-platform-WebhookHandlerFunction-* \
  --follow \
  --region us-east-1

# Watch reminder handler logs
aws logs tail /aws/lambda/telegram-bot-platform-ReminderHandlerFunction-* \
  --follow \
  --region us-east-1
```

### Check DynamoDB

```bash
# List tables
aws dynamodb list-tables --region us-east-1

# Scan tasks table
aws dynamodb scan \
  --table-name telegram-bot-tasks \
  --region us-east-1
```

## Updating the Bot

### Update Lambda Code

```bash
# Make changes to lambda/*/app.py
# Then rebuild and deploy
sam build && sam deploy
```

### Update Infrastructure

```bash
# Edit template.yaml
# Then redeploy
sam build && sam deploy
```

## Troubleshooting

### Webhook Not Working

```bash
# Check webhook status
BOT_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id telegram-bot-token \
  --query SecretString \
  --output text)

curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

### Lambda Errors

```bash
# View recent errors
aws logs filter-pattern \
  --log-group-name /aws/lambda/telegram-bot-platform-WebhookHandlerFunction-* \
  --filter-pattern "ERROR" \
  --region us-east-1
```

### DynamoDB Access Issues

Check IAM permissions in the Lambda execution role:
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:UpdateItem`

### EventBridge Scheduler Issues

Check if schedules are being created:

```bash
aws scheduler list-schedules --region us-east-1
```

## Cost Monitoring

```bash
# Check Lambda invocations (current month)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=telegram-bot-platform-WebhookHandlerFunction \
  --start-time $(date -u -d '1 month ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --region us-east-1
```

## Cleanup

To delete all resources:

```bash
# Delete SAM stack
sam delete --stack-name telegram-bot-platform --region us-east-1

# Delete bot token secret
aws secretsmanager delete-secret \
  --secret-id telegram-bot-token \
  --force-delete-without-recovery \
  --region us-east-1
```

## Production Best Practices

### 1. Enable CloudWatch Alarms

```bash
# Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name telegram-bot-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

### 2. Enable DynamoDB Point-in-Time Recovery

```bash
aws dynamodb update-continuous-backups \
  --table-name telegram-bot-tasks \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### 3. Set Up Budget Alerts

Use AWS Budgets to set spending limits and receive alerts.

### 4. Use Environment-Specific Stacks

```bash
# Development
sam deploy --stack-name telegram-bot-dev

# Production
sam deploy --stack-name telegram-bot-prod
```

## Architecture Diagram

```
Telegram User
     ↓
API Gateway (/webhook)
     ↓
Lambda: webhook_handler
     ↓
DynamoDB (tasks, users)
     ↓
EventBridge Scheduler
     ↓
Lambda: reminder_handler
     ↓
Telegram API (send message)
```

## Support

For issues or questions:
1. Check CloudWatch Logs
2. Review DynamoDB for data integrity
3. Verify IAM permissions
4. Check EventBridge schedules
