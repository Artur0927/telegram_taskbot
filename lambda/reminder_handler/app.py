"""
Reminder Handler - EventBridge-triggered Lambda
Sends task reminders when scheduled time arrives
"""

import json
import logging
import os

import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
scheduler_client = boto3.client('scheduler')

# Environment variables
TASKS_TABLE_NAME = os.environ['TASKS_TABLE_NAME']
BOT_TOKEN_SECRET = os.environ['BOT_TOKEN_SECRET']

# DynamoDB table
tasks_table = dynamodb.Table(TASKS_TABLE_NAME)

# Cache bot token
_bot_token_cache = None

def get_bot_token() -> str:
    """Get bot token from Secrets Manager (with caching)"""
    global _bot_token_cache

    if _bot_token_cache is None:
        response = secrets_client.get_secret_value(SecretId=BOT_TOKEN_SECRET)
        _bot_token_cache = response['SecretString']

    return _bot_token_cache


def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send message to Telegram user"""
    import urllib3
    http = urllib3.PoolManager()

    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        response = http.request(
            'POST',
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        return response.status == 200
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False


def lambda_handler(event, context):
    """
    EventBridge-triggered Lambda handler for sending reminders
    
    Event format:
    {
        "userId": 12345,
        "taskId": "uuid-here"
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        user_id = event['userId']
        task_id = event['taskId']

        # Fetch task from DynamoDB
        response = tasks_table.get_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )

        task = response.get('Item')

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            return {'statusCode': 404, 'body': 'Task not found'}

        # Skip if already notified or not pending
        if task.get('notified') or task.get('status') != 'pending':
            logger.info(f"Task {task_id} already processed")
            return {'statusCode': 200, 'body': 'Already processed'}

        # Send reminder
        reminder_text = (
            f"🔔 **Reminder**\n\n"
            f"{task['text']}\n\n"
            f"Mark as done: /done {task_id[:8]}"
        )

        success = send_telegram_message(user_id, reminder_text)

        if success:
            # Mark task as notified
            tasks_table.update_item(
                Key={
                    'userId': user_id,
                    'taskId': task_id
                },
                UpdateExpression='SET notified = :true',
                ExpressionAttributeValues={
                    ':true': True
                }
            )

            logger.info(f"Sent reminder for task {task_id} to user {user_id}")

        # Delete EventBridge schedule
        try:
            scheduler_client.delete_schedule(Name=f'reminder-{task_id}')
        except Exception as e:
            logger.warning(f"Failed to delete schedule: {e}")

        return {
            'statusCode': 200,
            'body': json.dumps({'success': success})
        }

    except Exception as e:
        logger.error(f"Error in reminder handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
