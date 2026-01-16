#!/bin/bash
# Fix CORS in API Gateway

API_ID="8oa74f9la7"
TASKS_RESOURCE="lv6xim"
PROFILE_RESOURCE="18sn1n"
REGION="us-east-1"

echo "🔧 Adding CORS headers to API Gateway..."

# Add CORS response for OPTIONS on /tasks
echo "Setting up OPTIONS response for /tasks..."
aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $TASKS_RESOURCE \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    "method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true" \
  --region $REGION 2>/dev/null || echo "Method response exists"

aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $TASKS_RESOURCE \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    "method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization',method.response.header.Access-Control-Allow-Methods='GET,POST,DELETE,OPTIONS',method.response.header.Access-Control-Allow-Origin='*'" \
  --region $REGION 2>/dev/null || echo "Integration response exists"

# Add CORS response for OPTIONS on /profile
echo "Setting up OPTIONS response for /profile..."
aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $PROFILE_RESOURCE \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    "method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true" \
  --region $REGION 2>/dev/null || echo "Method response exists"

aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $PROFILE_RESOURCE \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    "method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization',method.response.header.Access-Control-Allow-Methods='GET,OPTIONS',method.response.header.Access-Control-Allow-Origin='*'" \
  --region $REGION 2>/dev/null || echo "Integration response exists"

# Redeploy
echo "Redeploying API..."
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --region $REGION

echo "✅ CORS configured!"
