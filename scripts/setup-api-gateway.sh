#!/bin/bash
# Setup API Gateway for Mini App

set -e

API_ID="8oa74f9la7"
REGION="us-east-1"
LAMBDA_ARN="arn:aws:lambda:us-east-1:577713924485:function:miniapp-api"

echo "🔧 Настройка API Gateway..."

# Get root resource
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/`].id' --output text)

echo "Root resource ID: $ROOT_ID"

# Create /tasks resource
echo "Creating /tasks resource..."
TASKS_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part tasks \
  --region $REGION \
  --query 'id' --output text 2>&1 || echo "exists")

if [ "$TASKS_RESOURCE" = "exists" ]; then
  TASKS_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/tasks`].id' --output text)
fi

echo "Tasks resource ID: $TASKS_RESOURCE"

# Create /profile resource
echo "Creating /profile resource..."
PROFILE_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part profile \
  --region $REGION \
  --query 'id' --output text 2>&1 || echo "exists")

if [ "$PROFILE_RESOURCE" = "exists" ]; then
  PROFILE_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/profile`].id' --output text)
fi

echo "Profile resource ID: $PROFILE_RESOURCE"

# Configure methods for /tasks (GET, POST, OPTIONS)
for METHOD in GET POST OPTIONS; do
  echo "Setting up $METHOD /tasks..."
  aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $TASKS_RESOURCE \
    --http-method $METHOD \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "Method exists"
    
  if [ "$METHOD" != "OPTIONS" ]; then
    aws apigateway put-integration \
      --rest-api-id $API_ID \
      --resource-id $TASKS_RESOURCE \
      --http-method $METHOD \
      --type AWS_PROXY \
      --integration-http-method POST \
      --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
      --region $REGION 2>/dev/null || echo "Integration exists"
  fi
done

# Configure methods for /profile (GET, OPTIONS)
for METHOD in GET OPTIONS; do
  echo "Setting up $METHOD /profile..."
  aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $PROFILE_RESOURCE \
    --http-method $METHOD \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "Method exists"
    
  if [ "$METHOD" != "OPTIONS" ]; then
    aws apigateway put-integration \
      --rest-api-id $API_ID \
      --resource-id $PROFILE_RESOURCE \
      --http-method $METHOD \
      --type AWS_PROXY \
      --integration-http-method POST \
      --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
      --region $REGION 2>/dev/null || echo "Integration exists"
  fi
done

# Add Lambda permission
echo "Adding Lambda invoke permission..."
aws lambda add-permission \
  --function-name miniapp-api \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:577713924485:$API_ID/*" \
  --region $REGION 2>/dev/null || echo "Permission exists"

# Deploy API
echo "Deploying API to prod stage..."
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --region $REGION

echo ""
echo "✅ API Gateway настроен!"
echo ""
echo "API URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod"
echo ""
echo "Endpoints:"
echo "  GET  /tasks   - Get user tasks"
echo "  POST /tasks   - Create task"
echo "  GET  /profile - Get user profile"
