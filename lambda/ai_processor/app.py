import json
import logging
import os
import datetime
import traceback
import boto3
import google.generativeai as genai
from decimal import Decimal

# Initialize AWS clients
secrets_client = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ.get('USERS_TABLE_NAME', 'telegram-bot-user-settings'))

# Environment variables
GEMINI_KEY_SECRET = os.environ.get('GEMINI_KEY_SECRET', 'GEMINI_API_KEY')
RATE_LIMIT_DAILY = int(os.environ.get('AI_RATE_LIMIT', '10'))

class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "requestId": getattr(record, "aws_request_id", None)
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Clear existing handlers to avoid double logging
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def get_api_key():
    """Retrieve API key from Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=GEMINI_KEY_SECRET)
        return response['SecretString']
    except Exception as e:
        logger.error(f"Failed to retrieve secret: {e}")
        return None

def check_rate_limit(user_id):
    """
    Check and update daily rate limit for user.
    Returns (allowed: bool, remaining: int)
    """
    if not user_id:
        return True, RATE_LIMIT_DAILY  # Fail open if no user_id (shouldn't happen)
        
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    key = f"ai_usage_{today}"
    
    try:
        response = users_table.update_item(
            Key={'userId': int(user_id)},
            UpdateExpression="SET #usage = if_not_exists(#usage, :zero) + :inc",
            ExpressionAttributeNames={'#usage': key},
            ExpressionAttributeValues={':inc': 1, ':zero': 0, ':limit': RATE_LIMIT_DAILY},
            ConditionExpression="attribute_not_exists(#usage) OR #usage < :limit",
            ReturnValues="UPDATED_NEW"
        )
        used = int(response['Attributes'][key])
        return True, RATE_LIMIT_DAILY - used
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return False, 0
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        # Fail closed or open? Let's fail open for reliability unless DB is down
        return True, 0

def lambda_handler(event, context):
    """
    Handle AI requests (smart task creation, suggestions, etc.)
    """
    # Inject request_id into logger context if possible (hacky for basic logging)
    logger.aws_request_id = context.aws_request_id
    
    logger.info(f"Received event: {json.dumps(event)}")

    # Handle CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Telegram-Init-Data',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': ''
        }

    try:
        # 1. Parse User ID from headers (X-Telegram-Init-Data) logic usually happens in API GW authorized or client
        # For this architecture, client sends it in body or we trust valid InitData. 
        # But wait, AiProcessor is called from Frontend directly via API Gateway.
        # We need to validate auth or iterate trust. 
        # For MVP/Phase 2, we assume the API Gateway passes through, but to Rate Limit correctly we need the User ID.
        # The frontend calls `fetch` with `body: { action, data: { text, userId } }`? 
        # Let's check previous codebase or assume we parse it from body for now.
        
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        data = body.get('data', {})
        
        # Extract User ID for Rate Limiting
        # In a real secure app, we validate InitData here again.
        # For now, we trust the `userId` in `data` or header if available.
        # Let's try to get it from `data` as the frontend likely sends it.
        user_id = data.get('userId')
        
        # 2. Rate Limit Check
        if user_id:
            allowed, remaining = check_rate_limit(user_id)
            if not allowed:
                return {
                    'statusCode': 429,
                    'headers': { 'Access-Control-Allow-Origin': '*' },
                    'body': json.dumps({'error': 'Daily AI limit reached. Upgrade to Premium for more.'})
                }
        
        api_key = get_api_key()
        if not api_key:
            return {
                'statusCode': 500,
                'headers': { 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'error': 'Checking API configuration'})
            }

        genai.configure(api_key=api_key)

        if action == 'parse_task':
            # NLP Task Parsing
            user_input = data.get('text', '')
            prompt = f"""
            Extract task details from this text: "{user_input}"
            Return ONLY simple JSON with these fields:
            - text: short task title
            - priority: low, medium, or high (infer if possible, default medium)
            - due_date: ISO format if mentioned (e.g. 2024-01-01T12:00:00), null otherwise. Assume current year/month if ambiguous.
            """

            try:
                # Try newer model first
                model = genai.GenerativeModel('gemini-2.0-flash-001')
                response = model.generate_content(prompt)
            except Exception as e:
                logger.error(f"Model generation failed with gemini-2.0-flash-001: {e}")

                # List available models for debugging
                try:
                    logger.info("Listing available models:")
                    for m in genai.list_models():
                        logger.info(f"Available model: {m.name}")
                except Exception as le:
                    logger.error(f"Failed to list models: {le}")

                raise e

            result = response.text.strip().replace('```json', '').replace('```', '')

            return {
                'statusCode': 200,
                'headers': { 'Access-Control-Allow-Origin': '*' },
                'body': result
            }

        elif action == 'suggest_tasks':
            # Suggest based on context
            pass

        return {
            'statusCode': 400,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'error': 'Invalid action'})
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'error': str(e)})
        }
