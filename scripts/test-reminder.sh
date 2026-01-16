#!/bin/bash

# Test Reminder System
# Creates a test task with reminder in 2 minutes

USER_ID=1685847131  # Your demo user ID
TASK_TEXT="Test reminder - should notify in 2 minutes"
REMIND_TIME=$(date -u -v+2M +%s)  # 2 minutes from now

echo "Creating test task with reminder..."
echo "Task: $TASK_TEXT"
echo "Remind at: $(date -r $REMIND_TIME)"

# Create task via API
curl -X POST "https://8oa74f9la7.execute-api.us-east-1.amazonaws.com/prod/tasks" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$TASK_TEXT\",
    \"remindAt\": $REMIND_TIME,
    \"priority\": \"high\",
    \"tags\": [\"test\"]
  }"

echo ""
echo ""
echo "✅ Test task created!"
echo "⏰ You should receive Telegram notification in 2 minutes"
echo "📱 Check your Telegram: @MyJassistentBot"
