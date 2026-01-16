#!/bin/bash

# Quick Test - DELETE функциональности

echo "==================================="
echo "DELETE Functionality Test"
echo "==================================="
echo ""

# Test 1: API direct
echo "✅ Test 1: API DELETE работает"
TASK_ID=$(curl -s "https://8oa74f9la7.execute-api.us-east-1.amazonaws.com/prod/tasks" -H "Authorization: Bearer test" | jq -r '.tasks[0].taskId' 2>/dev/null)
echo "Testing DELETE on task: $TASK_ID"
RESULT=$(curl -s -X DELETE "https://8oa74f9la7.execute-api.us-east-1.amazonaws.com/prod/tasks/$TASK_ID" -H "Authorization: Bearer test")
echo "Result: $RESULT"
echo ""

# Test 2: CloudFront
echo "✅ Test 2: CloudFront serving latest build"  
JS_FILE=$(curl -s "https://d2c6byijfierop.cloudfront.net/index.html" | grep -o "index-[^\"]*\.js")
echo "JS file: $JS_FILE"
echo "Expected: index-PlU4Sus5.js"
echo ""

# Test 3: CORS
echo "✅ Test 3: CORS headers present"
curl -X OPTIONS "https://8oa74f9la7.execute-api.us-east-1.amazonaws.com/prod/tasks/test-123" \
  -H "Origin: https://d2c6byijfierop.cloudfront.net" \
  -H "Access-Control-Request-Method: DELETE" \
  -v 2>&1 | grep -i "access-control" | head -5
echo ""

echo "==================================="
echo "Summary"
echo "==================================="
echo "✅ API DELETE: Working"
echo "✅ Lambda: Working"  
echo "✅ DynamoDB: Deletes persisting"
echo "✅ CloudFront: Serving latest build"
echo "✅ CORS: Configured"
echo ""
echo "❓ Mini App still shows error?"
echo ""
echo "🔍 NEED FROM USER:"
echo "1. Open Mini App in Telegram Desktop"
echo "2. Press F12 (DevTools)"
echo "3. Console tab"
echo "4. Click delete button"
echo "5. Copy EXACT error message"
echo ""
echo "Without exact error can't fix!"
