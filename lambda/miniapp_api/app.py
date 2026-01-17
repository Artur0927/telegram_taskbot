"""
Mini App API Lambda Handler
Provides REST API for Telegram Mini App task management
"""
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment
TASKS_TABLE_NAME = os.environ.get('TASKS_TABLE_NAME', 'telegram-bot-tasks')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'telegram-bot-user-settings')

# DynamoDB
dynamodb = boto3.resource('dynamodb')
tasks_table = dynamodb.Table(TASKS_TABLE_NAME)
users_table = dynamodb.Table(USERS_TABLE_NAME)

# Scheduler
scheduler = boto3.client('scheduler')
REMINDER_LAMBDA_ARN = os.environ.get('REMINDER_LAMBDA_ARN')
SCHEDULER_ROLE_ARN = os.environ.get('SCHEDULER_ROLE_ARN')

# Bot token for validation
BOT_TOKEN_SECRET = os.environ.get('BOT_TOKEN_SECRET', 'telegram-bot-token')


def get_bot_token() -> str:
    """Get bot token from Secrets Manager"""
    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=BOT_TOKEN_SECRET)
        return response['SecretString']
    except Exception as e:
        logger.error(f"Error getting bot token: {e}")
        return ""


def validate_telegram_auth(init_data: str) -> Optional[int]:
    """Validate Telegram WebApp initData and return user_id"""
    try:
        # Parse init_data
        params = dict(p.split('=') for p in init_data.split('&') if '=' in p)

        if 'hash' not in params:
            return None

        received_hash = params.pop('hash')

        # Create data check string
        data_check_string = '\n'.join(
            f"{k}={params[k]}" for k in sorted(params.keys())
        )

        # Get bot token and create secret key
        bot_token = get_bot_token()
        secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()

        # Calculate hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash == received_hash:
            # Extract user_id from user parameter
            import urllib.parse
            user_data = json.loads(urllib.parse.unquote(params.get('user', '{}')))
            return user_data.get('id')

        return None
    except Exception as e:
        logger.error(f"Auth validation error: {e}")
        return None


def cors_response(status_code: int, body: Any) -> Dict:
    """Build CORS-enabled response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Telegram-Init-Data',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }


# ========================================
# GAMIFICATION (same as webhook_handler)
# ========================================

XP_REWARDS = {'low': 10, 'medium': 20, 'high': 30}
XP_STREAK_BONUS = 5
XP_DELETE_PENALTY = 10

ACHIEVEMENTS = {
    'first_task': {'name': '🎯 First Task', 'description': 'Complete your first task'},
    'week_streak': {'name': '🔥 Week Warrior', 'description': '7-day streak'},
    'early_bird': {'name': '🌅 Early Bird', 'description': 'Complete task before 8:00'},
    'night_owl': {'name': '🦉 Night Owl', 'description': 'Complete task after 22:00'},
    'century': {'name': '💯 Centurion', 'description': 'Complete 100 tasks'},
    'priority_master': {'name': '⚡ Priority Master', 'description': '10 high priority tasks'},
    'no_quit': {'name': '💪 No Quit', 'description': '30 days without deleting tasks'}
}


def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get user profile, create if not exists"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' in response:
            return response['Item']

        default_profile = {
            'userId': user_id,
            'level': 1,
            'totalXP': 0,
            'streak': 0,
            'tasksCompleted': 0,
            'highPriorityCompleted': 0,
            'achievements': [],
            'lastCompletedDate': None,
            'daysWithoutDelete': 0
        }
        users_table.put_item(Item=default_profile)
        return default_profile
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        # Ensure userId is returned even in error case if possible, or at least the input userId
        return {
            'userId': user_id,
            'level': 1,
            'totalXP': 0,
            'streak': 0,
            'tasksCompleted': 0,
            'achievements': []
        }


def check_achievements(profile: Dict[str, Any], current_hour: int = None) -> List[str]:
    """Check and unlock new achievements"""
    unlocked = []
    current_achievements = profile.get('achievements', [])

    tasks_completed = profile.get('tasksCompleted', 0)
    streak = profile.get('streak', 0)
    high_priority = profile.get('highPriorityCompleted', 0)
    days_no_delete = profile.get('daysWithoutDelete', 0)

    if current_hour is None:
        current_hour = datetime.utcnow().hour

    if 'first_task' not in current_achievements and tasks_completed >= 1:
        unlocked.append('first_task')
    if 'week_streak' not in current_achievements and streak >= 7:
        unlocked.append('week_streak')
    if 'early_bird' not in current_achievements and current_hour < 8:
        unlocked.append('early_bird')
    if 'night_owl' not in current_achievements and current_hour >= 22:
        unlocked.append('night_owl')
    if 'century' not in current_achievements and tasks_completed >= 100:
        unlocked.append('century')
    if 'priority_master' not in current_achievements and high_priority >= 10:
        unlocked.append('priority_master')
    if 'no_quit' not in current_achievements and days_no_delete >= 30:
        unlocked.append('no_quit')

    return unlocked


def award_xp(user_id: int, priority: str = 'medium') -> Dict[str, Any]:
    """Award XP for completing a task"""
    try:
        profile = get_user_profile(user_id)
        base_xp = XP_REWARDS.get(priority, 20)

        today = datetime.utcnow().date().isoformat()
        last_date = profile.get('lastCompletedDate')
        yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()

        if last_date == yesterday:
            new_streak = profile.get('streak', 0) + 1
        elif last_date == today:
            new_streak = profile.get('streak', 1)
        else:
            new_streak = 1

        streak_bonus = XP_STREAK_BONUS * (new_streak - 1) if new_streak > 1 else 0
        total_earned = base_xp + streak_bonus

        new_total_xp = int(profile.get('totalXP', 0)) + total_earned
        new_tasks_completed = profile.get('tasksCompleted', 0) + 1
        new_high_priority = profile.get('highPriorityCompleted', 0) + (1 if priority == 'high' else 0)

        old_level = profile.get('level', 1)
        new_level = (new_total_xp // 100) + 1
        level_up = new_level > old_level

        days_no_delete = profile.get('daysWithoutDelete', 0) + 1

        temp_profile = {
            **profile,
            'tasksCompleted': new_tasks_completed,
            'streak': new_streak,
            'highPriorityCompleted': new_high_priority,
            'daysWithoutDelete': days_no_delete
        }
        unlocked = check_achievements(temp_profile)
        achievement_xp = len(unlocked) * 50
        new_total_xp += achievement_xp

        # Activity Log
        activity_log = profile.get('activityLog', {})
        current_activity = int(activity_log.get(today, 0))
        activity_log[today] = current_activity + 1

        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='''SET 
                totalXP = :xp, #lvl = :level, streak = :streak,
                tasksCompleted = :tasks, highPriorityCompleted = :high,
                lastCompletedDate = :today, daysWithoutDelete = :noDelete,
                achievements = list_append(if_not_exists(achievements, :empty), :unlocked),
                activityLog = :activityLog
            ''',
            ExpressionAttributeNames={'#lvl': 'level'},
            ExpressionAttributeValues={
                ':xp': new_total_xp, ':level': new_level, ':streak': new_streak,
                ':tasks': new_tasks_completed, ':high': new_high_priority,
                ':today': today, ':noDelete': days_no_delete,
                ':unlocked': unlocked, ':empty': [],
                ':activityLog': activity_log
            }
        )

        return {
            'xp_earned': base_xp,
            'streak_bonus': streak_bonus,
            'achievement_xp': achievement_xp,
            'total_xp': new_total_xp,
            'new_level': new_level,
            'level_up': level_up,
            'streak': new_streak,
            'unlocked_achievements': [ACHIEVEMENTS[a]['name'] for a in unlocked]
        }
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        return {'xp_earned': 0, 'total_xp': 0, 'streak': 0, 'unlocked_achievements': []}


def penalize_xp(user_id: int) -> Dict[str, Any]:
    """Penalize XP for deleting task"""
    try:
        profile = get_user_profile(user_id)
        current_xp = int(profile.get('totalXP', 0))
        new_xp = max(0, current_xp - XP_DELETE_PENALTY)

        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET totalXP = :xp, daysWithoutDelete = :zero',
            ExpressionAttributeValues={':xp': new_xp, ':zero': 0}
        )

        return {'xp_lost': XP_DELETE_PENALTY, 'total_xp': new_xp}
    except Exception as e:
        logger.error(f"Error penalizing XP: {e}")
        return {'xp_lost': 0, 'total_xp': 0}


# ========================================
# REMINDER LOGIC
# ========================================

def create_reminder(user_id: int, task_id: str, text: str, remind_at: int):
    """Create EventBridge Schedule for reminder"""
    try:
        # Validate time (must be in future)
        now = datetime.utcnow().timestamp()
        if remind_at <= now:
            logger.info("Reminder time is in the past, skipping")
            return

        # Format time for Schedule (ISO 8601 usually required plain URL encoding or just string)
        # EventBridge Scheduler expects: yyyy-mm-ddThh:mm:ss
        dt_obj = datetime.fromtimestamp(remind_at)
        at_expression = f"at({dt_obj.strftime('%Y-%m-%dT%H:%M:%S')})"

        schedule_name = f"reminder-{task_id}"

        scheduler.create_schedule(
            Name=schedule_name,
            ScheduleExpression=at_expression,
            Target={
                'Arn': REMINDER_LAMBDA_ARN,
                'RoleArn': SCHEDULER_ROLE_ARN,
                'Input': json.dumps({
                    'userId': user_id,
                    'taskId': task_id,
                    'text': text
                })
            },
            FlexibleTimeWindow={'Mode': 'OFF'},
            ActionAfterCompletion='DELETE'
        )
        logger.info(f"Created schedule {schedule_name} for {at_expression}")
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")

def delete_reminder(task_id: str):
    """Delete EventBridge Schedule"""
    try:
        scheduler.delete_schedule(Name=f"reminder-{task_id}")
    except Exception as e:
        # Ignore if not found
        logger.info(f"Could not delete schedule/not found: {e}")


# ========================================
# API HANDLERS
# ========================================

def handle_get_tasks(user_id: int) -> Dict:
    """Get all tasks for user"""
    try:
        response = tasks_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id)
        )
        tasks = []
        for item in response.get('Items', []):
            tasks.append({
                'id': item.get('taskId'),
                'text': item.get('text', ''),
                'priority': item.get('priority', 'medium'),
                'status': item.get('status', 'pending'),
                'remindAt': int(item.get('remindAt', 0)),
                'tags': item.get('tags', []),
                'completedAt': int(item.get('completedAt', 0)) if item.get('completedAt') else None
            })
        return cors_response(200, {'tasks': tasks})
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return cors_response(500, {'error': 'Failed to get tasks'})


def handle_create_task(user_id: int, body: Dict) -> Dict:
    """Create new task"""
    try:
        task_id = str(uuid.uuid4())[:8]
        text = body.get('text', '')
        priority = body.get('priority', 'medium')
        
        remind_at_val = body.get('remindAt')
        if remind_at_val and str(remind_at_val).isdigit():
            remind_at = int(remind_at_val)
        else:
            # Default to 1 hour from now if missing or invalid
            remind_at = int(datetime.utcnow().timestamp()) + 3600

        tasks_table.put_item(Item={
            'userId': user_id,
            'taskId': task_id,
            'text': text,
            'priority': priority,
            'status': 'pending',
            'remindAt': Decimal(str(remind_at)),
            'tags': body.get('tags', []),
            'createdAt': Decimal(str(datetime.utcnow().timestamp()))
        })

        if remind_at:
             create_reminder(user_id, task_id, text, int(remind_at))

        return cors_response(201, {'taskId': task_id, 'message': 'Task created'})
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return cors_response(500, {'error': 'Failed to create task'})


def handle_complete_task(user_id: int, task_id: str) -> Dict:
    """Complete task and award XP"""
    try:
        response = tasks_table.get_item(Key={'userId': user_id, 'taskId': task_id})
        if 'Item' not in response:
            return cors_response(404, {'error': 'Task not found'})

        task = response['Item']
        priority = task.get('priority', 'medium')

        tasks_table.update_item(
            Key={'userId': user_id, 'taskId': task_id},
            UpdateExpression='SET #status = :done, completedAt = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':done': 'done',
                ':now': Decimal(str(datetime.utcnow().timestamp()))
            }
        )
        
        # Cleanup reminder
        delete_reminder(task_id)

        gamification = award_xp(user_id, priority)

        return cors_response(200, {
            'message': 'Task completed',
            'gamification': gamification
        })
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return cors_response(500, {'error': 'Failed to complete task'})


def handle_delete_task(user_id: int, task_id: str) -> Dict:
    """Delete task and penalize XP if not completed"""
    try:
        response = tasks_table.get_item(Key={'userId': user_id, 'taskId': task_id})
        if 'Item' not in response:
            return cors_response(404, {'error': 'Task not found'})

        task = response['Item']

        penalty = None
        if task.get('status') != 'done':
            penalty = penalize_xp(user_id)

        tasks_table.delete_item(Key={'userId': user_id, 'taskId': task_id})
        delete_reminder(task_id)

        return cors_response(200, {
            'message': 'Task deleted',
            'penalty': penalty
        })
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return cors_response(500, {'error': 'Failed to delete task'})


def handle_get_profile(user_id: int) -> Dict:
    """Get user profile with XP and achievements"""
    try:
        profile = get_user_profile(user_id)

        level = profile.get('level', 1)
        total_xp = int(profile.get('totalXP', 0))

        return cors_response(200, {
            'userId': user_id,
            'level': level,
            'totalXP': total_xp,
            'xpProgress': total_xp % 100,
            'xpForNextLevel': 100,
            'streak': profile.get('streak', 0),
            'tasksCompleted': profile.get('tasksCompleted', 0),
            'achievements': [
                {
                    'id': a,
                    'name': ACHIEVEMENTS.get(a, {}).get('name', a),
                    'description': ACHIEVEMENTS.get(a, {}).get('description', '')
                }
                for a in profile.get('achievements', [])
            ],
            'totalAchievements': len(ACHIEVEMENTS),
            'activityLog': profile.get('activityLog', {})
        })
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return cors_response(500, {'error': 'Failed to get profile'})


def handle_admin_stats(user_id: int) -> Dict:
    """Get global stats (Admin Only)"""
    # Security check - env var with fallback for safety
    admin_id = int(os.environ.get('ADMIN_USER_ID', '0'))
    
    if user_id != admin_id:
        return cors_response(403, {'error': 'Forbidden'})

    try:
        # Scan users table (ok for MVP)
        response = users_table.scan(
            ProjectionExpression='totalXP, tasksCompleted'
        )
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = users_table.scan(
                ProjectionExpression='totalXP, tasksCompleted',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        total_users = len(items)
        total_xp = sum(int(i.get('totalXP', 0)) for i in items)
        total_tasks = sum(int(i.get('tasksCompleted', 0)) for i in items)

        return cors_response(200, {
            'totalUsers': total_users,
            'totalXP': total_xp,
            'totalTasks': total_tasks
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        return cors_response(500, {'error': 'Failed to get stats'})


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """Main Lambda handler"""
    logger.info(f"Event: {json.dumps(event)}")

    # Handle OPTIONS (CORS preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return cors_response(200, {'message': 'OK'})

    # Get auth token from header
    headers = event.get('headers', {}) or {}
    query_params = event.get('queryStringParameters') or {}
    init_data = headers.get('X-Telegram-Init-Data') or headers.get('x-telegram-init-data', '')

    user_id = None
    if init_data:
        user_id = validate_telegram_auth(init_data)

    # Fallback for development (Restoring per user request for browser testing)
    if not user_id and query_params and query_params.get('userId'):
        try:
            user_id = int(query_params['userId'])
            logger.warning(f"⚠️ Using INSECURE fallback for userId: {user_id}")
        except ValueError:
            pass

    if not user_id:
        return cors_response(401, {'error': 'Unauthorized'})

    # Route requests
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    # Parse body for POST/PUT
    body = {}
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except:
            pass

    # Extract task_id from path
    path_params = event.get('pathParameters', {}) or {}
    task_id = path_params.get('taskId')

    # Routing
    if path == '/tasks' and method == 'GET':
        return handle_get_tasks(user_id)
    elif path == '/tasks' and method == 'POST':
        return handle_create_task(user_id, body)
    elif '/tasks/' in path and '/complete' in path and method == 'PUT':
        task_id = path.split('/tasks/')[1].split('/complete')[0]
        return handle_complete_task(user_id, task_id)
    elif '/tasks/' in path and method == 'DELETE':
        task_id = path.split('/tasks/')[1].rstrip('/')
        return handle_delete_task(user_id, task_id)
    elif path == '/profile' and method == 'GET':
        return handle_get_profile(user_id)
    elif path == '/admin/stats' and method == 'GET':
        return handle_admin_stats(user_id)
    else:
        return cors_response(404, {'error': 'Not found'})
