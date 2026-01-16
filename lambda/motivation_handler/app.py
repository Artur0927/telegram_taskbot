"""
Motivation Handler - Daily motivation message sender
Triggered by EventBridge cron schedule
"""

import json
import logging
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')

# Environment variables
USERS_TABLE_NAME = os.environ['USERS_TABLE_NAME']
MOTIVATION_TABLE_NAME = os.environ['MOTIVATION_TABLE_NAME']
BOT_TOKEN_SECRET = os.environ['BOT_TOKEN_SECRET']

# DynamoDB tables
users_table = dynamodb.Table(USERS_TABLE_NAME)
motivation_table = dynamodb.Table(MOTIVATION_TABLE_NAME)

# Cache bot token
_bot_token_cache = None

DEFAULT_MESSAGES = [
    "Small steps lead to big achievements. Keep going! 🌟",
    "Every task completed is progress. You're doing great!",
    "Focus on what you can control. One task at a time.",
    "Your consistency today builds your success tomorrow.",
    "Done is better than perfect. Just start!",
    "You don't have to be great to start, but you have to start to be great.",
    "The secret of getting ahead is getting started.",
    "Progress, not perfection. Keep moving forward.",
    "Your only limit is you. Break through it today!",
    "Success is the sum of small efforts repeated day in and day out."
]


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


def get_random_message() -> str:
    """Get random motivational message"""
    try:
        # Try to get from DynamoDB
        response = motivation_table.scan(Limit=50)
        messages = response.get('Items', [])

        if messages:
            return random.choice(messages)['text']
        else:
            # Fallback to default
            return random.choice(DEFAULT_MESSAGES)
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return random.choice(DEFAULT_MESSAGES)


def lambda_handler(event, context):
    """
    Daily motivation sender triggered by EventBridge
    """
    try:
        logger.info("Starting daily motivation send")

        # Scan users with motivation enabled
        response = users_table.scan(
            FilterExpression='motivationEnabled = :true',
            ExpressionAttributeValues={':true': True}
        )

        users = response.get('Items', [])
        logger.info(f"Found {len(users)} users with motivation enabled")

        now_ts = Decimal(str(datetime.utcnow().timestamp()))
        yesterday_ts = Decimal(str((datetime.utcnow() - timedelta(days=1)).timestamp()))

        sent_count = 0

        for user in users:
            user_id = int(user['userId'])
            last_motivation_at = user.get('lastMotivationAt', 0)

            # Check if already sent today
            if last_motivation_at > yesterday_ts:
                logger.info(f"Skipping user {user_id} - already sent today")
                continue

            # Get random message
            message_text = get_random_message()
            full_message = f"💪 **Daily Motivation**\n\n{message_text}"

            # Send message
            success = send_telegram_message(user_id, full_message)

            if success:
                # Update last_motivation_at
                users_table.update_item(
                    Key={'userId': user_id},
                    UpdateExpression='SET lastMotivationAt = :now',
                    ExpressionAttributeValues={':now': now_ts}
                )
                sent_count += 1
                logger.info(f"Sent motivation to user {user_id}")

        logger.info(f"Motivation send complete. Sent to {sent_count} users")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'sent_count': sent_count,
                'total_users': len(users)
            })
        }

    except Exception as e:
        logger.error(f"Error in motivation handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
