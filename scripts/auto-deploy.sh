#!/bin/bash
set -e

echo "🚀 Автоматический деплой Telegram бота на AWS Lambda"
echo ""

# Переменные
REGION="us-east-1"
BOT_TOKEN_SECRET="telegram-bot-token"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "📍 Регион: $REGION"
echo "🔑 AWS Account ID: $ACCOUNT_ID"
echo ""

# Шаг 1: Создание DynamoDB таблиц
echo "📦 Шаг 1/7: Создание DynamoDB таблиц..."

# Tasks таблица
aws dynamodb create-table \
  --table-name telegram-bot-tasks \
  --attribute-definitions \
    AttributeName=userId,AttributeType=N \
    AttributeName=taskId,AttributeType=S \
    AttributeName=status,AttributeType=S \
    AttributeName=remindAt,AttributeType=N \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=taskId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[{\"IndexName\":\"RemindersIndex\",\"KeySchema\":[{\"AttributeName\":\"status\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"remindAt\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]" \
  --region $REGION 2>/dev/null || echo "  ✓ telegram-bot-tasks уже существует"

# Users таблица
aws dynamodb create-table \
  --table-name telegram-bot-user-settings \
  --attribute-definitions AttributeName=userId,AttributeType=N \
  --key-schema AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  ✓ telegram-bot-user-settings уже существует"

# Motivation таблица
aws dynamodb create-table \
  --table-name telegram-bot-motivational-messages \
  --attribute-definitions AttributeName=messageId,AttributeType=S \
  --key-schema AttributeName=messageId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  ✓ telegram-bot-motivational-messages уже существует"

echo "✅ DynamoDB таблицы созданы"
echo ""

# Шаг 2: Создание IAM роли для Lambda
echo "🔐 Шаг 2/7: Создание IAM роли..."

# Trust policy для Lambda
cat > /tmp/lambda-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Создание роли
aws iam create-role \
  --role-name TelegramBotLambdaRole \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
  2>/dev/null || echo "  ✓ Роль уже существует"

# Добавление политик
aws iam attach-role-policy \
  --role-name TelegramBotLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  2>/dev/null || true

aws iam attach-role-policy \
  --role-name TelegramBotLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess \
  2>/dev/null || true

aws iam attach-role-policy \
  --role-name TelegramBotLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \
  2>/dev/null || true

# Inline policy для EventBridge
cat > /tmp/eventbridge-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "scheduler:CreateSchedule",
        "scheduler:DeleteSchedule",
        "scheduler:GetSchedule",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name TelegramBotLambdaRole \
  --policy-name EventBridgeSchedulerPolicy \
  --policy-document file:///tmp/eventbridge-policy.json \
  2>/dev/null || true

echo "✅ IAM роль создана"
echo ""

# Ждем создания роли
echo "⏳ Ожидание 10 секунд для создания IAM роли..."
sleep 10

# Шаг 3: Создание Lambda функций
echo "⚡ Шаг 3/7: Создание Lambda функций..."

ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/TelegramBotLambdaRole"

# Reminder Handler
aws lambda create-function \
  --function-name reminder-handler \
  --runtime python3.9 \
  --role $ROLE_ARN \
  --handler app.lambda_handler \
  --zip-file fileb://deployment-packages/reminder_handler.zip \
  --timeout 10 \
  --memory-size 256 \
  --environment "Variables={TASKS_TABLE_NAME=telegram-bot-tasks,BOT_TOKEN_SECRET=$BOT_TOKEN_SECRET}" \
  --region $REGION \
  2>/dev/null || aws lambda update-function-code \
    --function-name reminder-handler \
    --zip-file fileb://deployment-packages/reminder_handler.zip \
    --region $REGION

REMINDER_ARN=$(aws lambda get-function --function-name reminder-handler --region $REGION --query 'Configuration.FunctionArn' --output text)

echo "  ✓ reminder-handler создан: $REMINDER_ARN"

# Webhook Handler
aws lambda create-function \
  --function-name webhook-handler \
  --runtime python3.9 \
  --role $ROLE_ARN \
  --handler app.lambda_handler \
  --zip-file fileb://deployment-packages/webhook_handler.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment "Variables={TASKS_TABLE_NAME=telegram-bot-tasks,USERS_TABLE_NAME=telegram-bot-user-settings,MOTIVATION_TABLE_NAME=telegram-bot-motivational-messages,BOT_TOKEN_SECRET=$BOT_TOKEN_SECRET,REMINDER_LAMBDA_ARN=$REMINDER_ARN,EVENTBRIDGE_ROLE_ARN=$ROLE_ARN}" \
  --region $REGION \
  2>/dev/null || aws lambda update-function-code \
    --function-name webhook-handler \
    --zip-file fileb://deployment-packages/webhook_handler.zip \
    --region $REGION

echo "  ✓ webhook-handler создан"

# Motivation Handler  
aws lambda create-function \
  --function-name motivation-handler \
  --runtime python3.9 \
  --role $ROLE_ARN \
  --handler app.lambda_handler \
  --zip-file fileb://deployment-packages/motivation_handler.zip \
  --timeout 60 \
  --memory-size 256 \
  --environment "Variables={USERS_TABLE_NAME=telegram-bot-user-settings,MOTIVATION_TABLE_NAME=telegram-bot-motivational-messages,BOT_TOKEN_SECRET=$BOT_TOKEN_SECRET}" \
  --region $REGION \
  2>/dev/null || aws lambda update-function-code \
    --function-name motivation-handler \
    --zip-file fileb://deployment-packages/motivation_handler.zip \
    --region $REGION

echo "  ✓ motivation-handler создан"
echo "✅ Lambda функции созданы"
echo ""

# Шаг 4: Создание API Gateway
echo "🌐 Шаг 4/7: Создание API Gateway..."

# Создание REST API
API_ID=$(aws apigateway create-rest-api \
  --name telegram-bot-api \
  --region $REGION \
  --query 'id' \
  --output text 2>/dev/null) || API_ID=$(aws apigateway get-rest-apis \
    --region $REGION \
    --query "items[?name=='telegram-bot-api'].id" \
    --output text)

echo "  ✓ API ID: $API_ID"

# Получить root resource
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --region $REGION \
  --query 'items[?path==`/`].id' \
  --output text)

# Создать resource /webhook
WEBHOOK_RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part webhook \
  --region $REGION \
  --query 'id' \
  --output text 2>/dev/null) || WEBHOOK_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query "items[?path=='/webhook'].id" \
    --output text)

echo "  ✓ Webhook resource ID: $WEBHOOK_RESOURCE_ID"

# Создать POST метод
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE \
  --region $REGION \
  2>/dev/null || true

# Интеграция с Lambda
LAMBDA_URI="arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT_ID:function:webhook-handler/invocations"

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri $LAMBDA_URI \
  --region $REGION \
  2>/dev/null || true

# Дать API Gateway разрешение вызывать Lambda
aws lambda add-permission \
  --function-name webhook-handler \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/*" \
  --region $REGION \
  2>/dev/null || true

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --region $REGION \
  2>/dev/null || true

WEBHOOK_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/prod/webhook"

echo "  ✓ API Gateway URL: $WEBHOOK_URL"
echo "✅ API Gateway создан"
echo ""

# Шаг 5: Установка Telegram webhook
echo "📱 Шаг 5/7: Установка Telegram webhook..."

BOT_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id $BOT_TOKEN_SECRET \
  --region $REGION \
  --query SecretString \
  --output text)

WEBHOOK_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=${WEBHOOK_URL}")

echo "  Response: $WEBHOOK_RESPONSE"
echo "✅ Webhook установлен"
echo ""

# Шаг 6: Создание EventBridge правила для мотивации
echo "📅 Шаг 6/7: Создание EventBridge правила..."

aws events put-rule \
  --name daily-motivation \
  --schedule-expression "cron(0 9 * * ? *)" \
  --region $REGION \
  2>/dev/null || true

aws events put-targets \
  --rule daily-motivation \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:motivation-handler" \
  --region $REGION \
  2>/dev/null || true

aws lambda add-permission \
  --function-name motivation-handler \
  --statement-id eventbridge-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/daily-motivation" \
  --region $REGION \
  2>/dev/null || true

echo "✅ EventBridge правило создано"
echo ""

# Шаг 7: Проверка
echo "🔍 Шаг 7/7: Проверка деплоя..."

WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
echo "  Webhook Info: $WEBHOOK_INFO"

echo ""
echo "🎉 ================================"
echo "🎉  ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "🎉 ================================"
echo ""
echo "📋 Информация о деплое:"
echo "  • Webhook URL: $WEBHOOK_URL"
echo "  • Lambda функции: webhook-handler, reminder-handler, motivation-handler"
echo "  • DynamoDB таблицы: 3 шт"
echo "  • Стоимость: ~\$2/месяц"
echo ""
echo "✅ Откройте Telegram и отправьте боту /start"
echo ""
