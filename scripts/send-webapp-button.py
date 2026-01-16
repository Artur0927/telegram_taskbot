"""
Add Web App button to Telegram bot
Allows users to open TaskBot Mini App directly from chat
"""

import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BOT_TOKEN_SECRET = os.environ.get('BOT_TOKEN_SECRET', 'telegram-bot-token')
MINIAPP_URL = os.environ.get('MINIAPP_URL', 'https://telegram-bot-miniapp-prod.s3.amazonaws.com/index.html')

secrets_client = boto3.client('secretsmanager')

def get_bot_token():
    """Get bot token from Secrets Manager"""
    response = secrets_client.get_secret_value(SecretId=BOT_TOKEN_SECRET)
    return response['SecretString']


def send_message_with_webapp(chat_id: int, bot_token: str):
    """Send message with Web App button"""
    import urllib3
    
    http = urllib3.PoolManager()
    
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🏭 Open TaskBot",
                "web_app": {"url": MINIAPP_URL}
            }
        ]]
    }
    
    message = (
        "🏭 <b>NetFactory TaskBot Mini App</b>\n\n"
        "✨ Open the app for rich visual interface:\n"
        "• 📋 Kanban task board\n"
        "• 📅 Visual calendar\n"
        "• 🎮 Profile with XP & achievements\n\n"
        "Click the button below to start! 👇"
    )
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(keyboard)
    }
    
    response = http.request(
        'POST',
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        fields=data
    )
    
    return response.status == 200


if __name__ == '__main__':
    # Test sending to your user ID
    bot_token = get_bot_token()
    user_id = 1685847131  # Your Telegram user ID
    
    success = send_message_with_webapp(user_id, bot_token)
    print(f"Message sent: {success}")
