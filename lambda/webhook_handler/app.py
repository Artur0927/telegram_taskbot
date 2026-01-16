"""
Telegram Webhook Handler - Main Lambda Function
Handles all incoming Telegram updates
Enhanced with: tags, priorities, snooze, smart parsing, stats, recurring
Phase 1 + Phase 2 features
"""

import json
import logging
import os
import re
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secretsmanager_client = boto3.client('secretsmanager')
scheduler_client = boto3.client('scheduler')
lambda_client = boto3.client('lambda')  # NEW: For AI processor

# Environment variables
TASKS_TABLE_NAME = os.environ['TASKS_TABLE_NAME']
USERS_TABLE_NAME = os.environ['USERS_TABLE_NAME']
MOTIVATION_TABLE_NAME = os.environ['MOTIVATION_TABLE_NAME']
BOT_TOKEN_SECRET = os.environ['BOT_TOKEN_SECRET']
REMINDER_LAMBDA_ARN = os.environ['REMINDER_LAMBDA_ARN']
AI_PROCESSOR_ARN = os.environ.get('AI_PROCESSOR_ARN', 'arn:aws:lambda:us-east-1:577713924485:function:ai-processor')
GAMIFICATION_ARN = os.environ.get('GAMIFICATION_ARN', 'arn:aws:lambda:us-east-1:577713924485:function:gamification-handler')  # NEW
SCHEDULER_ROLE_ARN = os.environ.get('SCHEDULER_ROLE_ARN', 'arn:aws:iam::577713924485:role/EventBridgeSchedulerRole')

# DynamoDB tables
tasks_table = dynamodb.Table(TASKS_TABLE_NAME)
users_table = dynamodb.Table(USERS_TABLE_NAME)
motivation_table = dynamodb.Table(MOTIVATION_TABLE_NAME)

# Cache bot token
_bot_token_cache = None

def get_bot_token() -> str:
    """Get bot token from Secrets Manager (with caching)"""
    global _bot_token_cache

    if _bot_token_cache is None:
        response = secretsmanager_client.get_secret_value(SecretId=BOT_TOKEN_SECRET)
        _bot_token_cache = response['SecretString']

    return _bot_token_cache


def schedule_reminder(user_id: int, task_id: str, remind_at: int) -> bool:
    """Create EventBridge Scheduler schedule to trigger reminder at specified time"""
    try:
        from datetime import datetime

        # Convert Unix timestamp to ISO-8601 format for EventBridge
        remind_datetime = datetime.utcfromtimestamp(remind_at)
        schedule_time = remind_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        # Get EventBridge Scheduler role ARN
        scheduler_role_arn = SCHEDULER_ROLE_ARN

        # Create one-time schedule
        schedule_name = f"reminder-{task_id}"

        scheduler_client.create_schedule(
            Name=schedule_name,
            ScheduleExpression=f'at({schedule_time})',
            ScheduleExpressionTimezone='UTC',
            FlexibleTimeWindow={'Mode': 'OFF'},
            Target={
                'Arn': REMINDER_LAMBDA_ARN,
                'RoleArn': scheduler_role_arn,
                'Input': json.dumps({
                    'userId': user_id,
                    'taskId': task_id
                })
            },
            State='ENABLED'
        )

        logger.info(f"Created reminder schedule {schedule_name} for {schedule_time} UTC")
        return True

    except Exception as e:
        logger.error(f"Failed to create reminder schedule: {e}")
        return False


def call_ai_processor(action: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call AI processor Lambda function"""
    try:
        payload = {'action': action, **data}
        response = lambda_client.invoke(
            FunctionName=AI_PROCESSOR_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())
        if result.get('statusCode') == 200:
            return json.loads(result['body'])
        else:
            logger.error(f"AI processor error: {result}")
            return None
    except Exception as e:
        logger.error(f"Error calling AI processor: {e}")
        return None


# Utility functions
def parse_tags(text: str) -> List[str]:
    """Extract hashtags from text"""
    tags = re.findall(r'#(\w+)', text)
    return list(set(tags))


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level"""
    return {
        'high': '🔴',
        'medium': '🟡',
        'low': '⚪'
    }.get(priority, '⚪')


def parse_snooze_delay(delay_str: str) -> int:
    """Parse snooze delay to timestamp"""
    now = datetime.utcnow()
    delay_str = delay_str.lower().strip()

    if match := re.match(r'(\d+)h', delay_str):
        target = now + timedelta(hours=int(match.group(1)))
    elif match := re.match(r'(\d+)m(?:in)?', delay_str):
        target = now + timedelta(minutes=int(match.group(1)))
    elif 'tomorrow' in delay_str or 'завтра' in delay_str:
        target = now + timedelta(days=1)
    elif 'week' in delay_str:
        target = now + timedelta(days=7)
    else:
        target = now + timedelta(hours=1)

    return int(target.timestamp())


def parse_smart_time(text: str) -> Optional[datetime]:
    """Enhanced time parsing"""
    text_lower = text.lower()
    now = datetime.utcnow()

    # "in X hours/minutes"
    if match := re.search(r'in (\d+) ?(h|hour|hours)', text_lower):
        return now + timedelta(hours=int(match.group(1)))

    if match := re.search(r'in (\d+) ?(m|min|minute|minutes)', text_lower):
        return now + timedelta(minutes=int(match.group(1)))

    # Days of week
    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'понедельник': 0, 'вторник': 1, 'среда': 2, 'четверг': 3,
        'пятница': 4, 'суббота': 5, 'воскресенье': 6
    }

    for day_name, day_num in days_map.items():
        if day_name in text_lower:
            current_day = now.weekday()
            days_ahead = (day_num - current_day) % 7 or 7
            target_date = now + timedelta(days=days_ahead)

            time_match = re.search(r'(\d{1,2}):(\d{2})', text)
            if time_match:
                hour, minute = int(time_match.group(1)), int(time_match.group(2))
                return target_date.replace(hour=hour, minute=minute, second=0)
            return target_date.replace(hour=9, minute=0, second=0)

    # Tomorrow
    if 'tomorrow' in text_lower or 'завтра' in text_lower:
        target = now + timedelta(days=1)
        time_match = re.search(r'(\d{1,2}):(\d{2})', text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            return target.replace(hour=hour, minute=minute, second=0)
        return target.replace(hour=9, minute=0, second=0)

    # Just time (HH:MM)
    if time_match := re.search(r'(\d{1,2}):(\d{2})', text):
        hour, minute = int(time_match.group(1)), int(time_match.group(2))
        target = now.replace(hour=hour, minute=minute, second=0)
        if target < now:
            target += timedelta(days=1)
        return target

    return None


# ========================================
# GAMIFICATION SYSTEM (Integrated)
# ========================================

XP_REWARDS = {
    'low': 10,
    'medium': 20,
    'high': 30
}
XP_STREAK_BONUS = 5
XP_DELETE_PENALTY = 10
XP_IGNORE_PENALTY = 15

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

        # Create default profile
        default_profile = {
            'userId': user_id,
            'level': 1,
            'totalXP': 0,
            'streak': 0,
            'tasksCompleted': 0,
            'highPriorityCompleted': 0,
            'achievements': [],
            'lastCompletedDate': None,
            'lastDeleteDate': None,
            'daysWithoutDelete': 0
        }
        users_table.put_item(Item=default_profile)
        return default_profile
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return {'userId': user_id, 'level': 1, 'totalXP': 0, 'streak': 0, 'tasksCompleted': 0, 'achievements': []}


def check_achievements(user_id: int, profile: Dict[str, Any], current_hour: int = None) -> List[str]:
    """Check and unlock new achievements"""
    unlocked = []
    current_achievements = profile.get('achievements', [])

    tasks_completed = profile.get('tasksCompleted', 0)
    streak = profile.get('streak', 0)
    high_priority = profile.get('highPriorityCompleted', 0)
    days_no_delete = profile.get('daysWithoutDelete', 0)

    if current_hour is None:
        current_hour = datetime.utcnow().hour

    # First Task
    if 'first_task' not in current_achievements and tasks_completed >= 1:
        unlocked.append('first_task')

    # Week Warrior (7 day streak)
    if 'week_streak' not in current_achievements and streak >= 7:
        unlocked.append('week_streak')

    # Early Bird (before 8 AM)
    if 'early_bird' not in current_achievements and current_hour < 8:
        unlocked.append('early_bird')

    # Night Owl (after 10 PM)
    if 'night_owl' not in current_achievements and current_hour >= 22:
        unlocked.append('night_owl')

    # Centurion (100 tasks)
    if 'century' not in current_achievements and tasks_completed >= 100:
        unlocked.append('century')

    # Priority Master (10 high priority)
    if 'priority_master' not in current_achievements and high_priority >= 10:
        unlocked.append('priority_master')

    # No Quit (30 days without delete)
    if 'no_quit' not in current_achievements and days_no_delete >= 30:
        unlocked.append('no_quit')

    return unlocked


def award_xp(user_id: int, priority: str = 'medium') -> Dict[str, Any]:
    """Award XP for completing a task"""
    try:
        profile = get_user_profile(user_id)

        # Calculate XP
        base_xp = XP_REWARDS.get(priority, 20)

        # Update streak
        today = datetime.utcnow().date().isoformat()
        last_date = profile.get('lastCompletedDate')
        yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()

        if last_date == yesterday:
            new_streak = profile.get('streak', 0) + 1
        elif last_date == today:
            new_streak = profile.get('streak', 1)  # Same day, keep streak
        else:
            new_streak = 1  # Streak broken

        streak_bonus = XP_STREAK_BONUS * (new_streak - 1) if new_streak > 1 else 0
        total_earned = base_xp + streak_bonus

        new_total_xp = int(profile.get('totalXP', 0)) + total_earned
        new_tasks_completed = profile.get('tasksCompleted', 0) + 1
        new_high_priority = profile.get('highPriorityCompleted', 0) + (1 if priority == 'high' else 0)

        # Calculate level (100 XP per level)
        old_level = profile.get('level', 1)
        new_level = (new_total_xp // 100) + 1
        level_up = new_level > old_level

        # Days without delete
        days_no_delete = profile.get('daysWithoutDelete', 0) + 1

        # Check achievements
        temp_profile = {
            **profile,
            'tasksCompleted': new_tasks_completed,
            'streak': new_streak,
            'highPriorityCompleted': new_high_priority,
            'daysWithoutDelete': days_no_delete
        }
        unlocked = check_achievements(user_id, temp_profile)

        # Achievement XP bonus
        achievement_xp = len(unlocked) * 50
        new_total_xp += achievement_xp

        # Update profile
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='''SET 
                totalXP = :xp,
                #lvl = :level,
                streak = :streak,
                tasksCompleted = :tasks,
                highPriorityCompleted = :high,
                lastCompletedDate = :today,
                daysWithoutDelete = :noDelete,
                achievements = list_append(if_not_exists(achievements, :empty), :unlocked)
            ''',
            ExpressionAttributeNames={'#lvl': 'level'},
            ExpressionAttributeValues={
                ':xp': new_total_xp,
                ':level': new_level,
                ':streak': new_streak,
                ':tasks': new_tasks_completed,
                ':high': new_high_priority,
                ':today': today,
                ':noDelete': days_no_delete,
                ':unlocked': unlocked,
                ':empty': []
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


def penalize_xp(user_id: int, reason: str = 'delete') -> Dict[str, Any]:
    """Penalize XP for deleting task or ignoring reminder"""
    try:
        profile = get_user_profile(user_id)

        penalty = XP_DELETE_PENALTY if reason == 'delete' else XP_IGNORE_PENALTY
        current_xp = int(profile.get('totalXP', 0))
        new_xp = max(0, current_xp - penalty)

        # Reset days without delete counter
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET totalXP = :xp, daysWithoutDelete = :zero, lastDeleteDate = :today',
            ExpressionAttributeValues={
                ':xp': new_xp,
                ':zero': 0,
                ':today': datetime.utcnow().date().isoformat()
            }
        )

        return {
            'xp_lost': penalty,
            'total_xp': new_xp,
            'reason': reason
        }
    except Exception as e:
        logger.error(f"Error penalizing XP: {e}")
        return {'xp_lost': 0, 'total_xp': 0}


def send_telegram_message(user_id: int, text: str, keyboard: dict = None) -> bool:
    """Send message to Telegram user"""
    import urllib3

    bot_token = get_bot_token()
    http = urllib3.PoolManager()

    data = {
        'chat_id': user_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)

    try:
        response = http.request(
            'POST',
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            fields=data
        )
        return response.status == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False


# Command Handlers
def handle_start(user_id: int) -> str:
    """Handle /start command"""
    return (
        "👋 **Welcome to Advanced TaskBot!**\n\n"
        "I'll help you manage tasks efficiently.\n\n"
        "**Quick Start:**\n"
        "• \"Meeting in 2 hours #work\"\n"
        "• \"Buy milk Friday 18:00 #personal\"\n"
        "• \"Call dentist tomorrow 14:00\"\n\n"
        "**Commands:**\n"
        "/tasks - View all tasks\n"
        "/tasks #work - Filter by tag\n"
        "/urgent <task> - High priority task\n"
        "/snooze <id> 1h - Delay task\n"
        "/stats - Your statistics\n"
        "/tags - List all tags\n"
        "/help - Detailed guide"
    )


def handle_app(user_id: int) -> dict:
    """Send Web App button with auth token"""
    # Generate one-time token
    token = secrets.token_urlsafe(32)

    # Store token in DynamoDB with expiry (5 minutes)
    try:
        users_table.put_item(
            Item={
                'userId': user_id,
                'token': token,
                'tokenExpiry': Decimal(str((datetime.utcnow() + timedelta(minutes=5)).timestamp())),
                'tokenUsed': False
            }
        )
        logger.info(f"Generated token for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to store token: {e}")
        token = ''  # Fallback to no token

    # Add token to URL
    miniapp_url = f"https://d2c6byijfierop.cloudfront.net?token={token}"

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🏭 Open TaskBot Mini App",
                "web_app": {"url": miniapp_url}
            }
        ]]
    }

    return {
        "text": (
            "🏭 <b>NetFactory TaskBot Mini App</b>\n\n"
            "✨ Rich visual interface:\n"
            "• 📋 Kanban task board\n"
            "• 📅 Visual calendar\n"
            "• 🎮 Profile with XP & achievements\n"
            "• ➕ Create/edit tasks with beautiful UI\n\n"
            "Click below to open! 👇"
        ),
        "keyboard": keyboard
    }


def handle_help(user_id: int) -> str:
    """Handle /help command"""
    return (
        "**📖 TaskBot Guide**\n\n"
        "**Smart Time:**\n"
        "• \"in 2 hours\" / \"через 2 часа\"\n"
        "• \"Monday 14:00\" / \"в понедельник\"\n"
        "• \"tomorrow\" / \"завтра\"\n\n"
        "**Tags & Priority:**\n"
        "• Add #tags in text\n"
        "• /urgent for high priority\n\n"
        "**🎮 Gamification:**\n"
        "• Complete tasks = +XP\n"
        "• Delete tasks = -XP penalty\n"
        "• Daily streak = bonus XP\n"
        "• Unlock achievements!\n\n"
        "📱 <b>Mini App:</b>\n"
        "Use /app for visual interface\n\n"
        "**Commands:**\n"
        "/app - Open Mini App\n"
        "/tasks - All tasks\n"
        "/done <id> - Complete task\n"
        "/delete <id> - Delete task\n"
        "/profile - XP & achievements\n"
        "/stats - Statistics\n"
        "/snooze <id> 1h - Delay"
    )


def handle_tasks_list(user_id: int, filter_tag: str = None) -> str:
    """List tasks with optional tag filter"""
    try:
        query_params = {
            'KeyConditionExpression': 'userId = :uid',
            'FilterExpression': '#status = :status',
            'ExpressionAttributeNames': {'#status': 'status'},
            'ExpressionAttributeValues': {':uid': user_id, ':status': 'pending'}
        }

        if filter_tag:
            tag = filter_tag.replace('#', '')
            query_params['FilterExpression'] += ' AND contains(tags, :tag)'
            query_params['ExpressionAttributeValues'][':tag'] = tag

        response = tasks_table.query(**query_params)
        tasks = response.get('Items', [])

        if not tasks:
            tag_msg = f" with tag {filter_tag}" if filter_tag else ""
            return f"📋 No pending tasks{tag_msg}.\n\nCreate one!"

        # Sort by priority then time
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        tasks.sort(key=lambda x: (priority_order.get(x.get('priority', 'medium'), 1), x['remindAt']))

        output = f"📋 **Your Tasks** ({len(tasks)}):\n\n"

        for task in tasks:
            remind_dt = datetime.fromtimestamp(int(task['remindAt']))
            priority_emoji = get_priority_emoji(task.get('priority', 'medium'))
            tags = task.get('tags', [])
            tags_str = ' ' + ' '.join(f'#{t}' for t in tags) if tags else ''

            output += (
                f"{priority_emoji} **{task['taskId'][:8]}** {task['text']}{tags_str}\n"
                f"   ⏰ {remind_dt.strftime('%d.%m.%Y at %H:%M')}\n\n"
            )

        return output
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return "❌ Failed to list tasks"


def handle_profile(user_id: int) -> str:
    """Get user profile with XP and achievements"""
    try:
        profile = get_user_profile(user_id)

        level = profile.get('level', 1)
        total_xp = int(profile.get('totalXP', 0))
        streak = profile.get('streak', 0)
        tasks_completed = profile.get('tasksCompleted', 0)
        achievements = profile.get('achievements', [])

        # Calculate XP for next level (100 XP per level)
        xp_in_level = total_xp % 100
        xp_for_next = 100
        progress_pct = int((xp_in_level / xp_for_next) * 100)

        # Format achievements using global ACHIEVEMENTS dict
        achievements_str = '\n'.join([ACHIEVEMENTS.get(a, {}).get('name', a) for a in achievements])
        if not achievements_str:
            achievements_str = 'No achievements yet'

        total_achievements = len(ACHIEVEMENTS)
        unlocked_count = len(achievements)

        return (
            f"👤 <b>Your Profile</b>\n\n"
            f"⭐ Level: {level}\n"
            f"💎 Total XP: {total_xp}\n"
            f"📊 Progress: {xp_in_level}/{xp_for_next} XP ({progress_pct}%)\n"
            f"🔥 Streak: {streak} days\n"
            f"✅ Tasks completed: {tasks_completed}\n\n"
            f"🏆 <b>Achievements ({unlocked_count}/{total_achievements}):</b>\n{achievements_str}"
        )
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return "❌ Error getting profile"


def handle_done(user_id: int, task_id: str) -> str:
    """Mark task as complete and award XP"""
    try:
        # Get task first to know priority
        response = tasks_table.get_item(Key={'userId': user_id, 'taskId': task_id})
        if 'Item' not in response:
            return "⚠️ Task not found"

        task = response['Item']
        priority = task.get('priority', 'medium')

        # Mark as done
        tasks_table.update_item(
            Key={'userId': user_id, 'taskId': task_id},
            UpdateExpression='SET #status = :done, completedAt = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':done': 'done',
                ':now': Decimal(str(datetime.utcnow().timestamp()))
            }
        )

        # Award XP using local gamification system
        gamification = award_xp(user_id, priority)

        xp_earned = gamification.get('xp_earned', 0)
        streak_bonus = gamification.get('streak_bonus', 0)
        achievement_xp = gamification.get('achievement_xp', 0)
        total_xp = gamification.get('total_xp', 0)
        new_level = gamification.get('new_level', 1)
        level_up = gamification.get('level_up', False)
        streak = gamification.get('streak', 0)
        unlocked = gamification.get('unlocked_achievements', [])

        response_msg = "✅ Task completed!\n\n"
        response_msg += f"+{xp_earned} XP"

        if streak_bonus > 0:
            response_msg += f" (+{streak_bonus} streak bonus)"

        if streak > 1:
            response_msg += f"\n🔥 {streak}-day streak!"

        if unlocked:
            for ach in unlocked:
                response_msg += f"\n\n🏆 Achievement unlocked: {ach}"
            if achievement_xp:
                response_msg += f" (+{achievement_xp} XP)"

        if level_up:
            response_msg += f"\n\n🎉 LEVEL UP! You're now level {new_level}!"

        response_msg += f"\n\n💎 Total XP: {total_xp}"
        return response_msg

    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return "⚠️ Error completing task"


def handle_delete_task(user_id: int, task_id: str) -> str:
    """Delete task and penalize XP"""
    try:
        # Check if task exists
        response = tasks_table.get_item(Key={'userId': user_id, 'taskId': task_id})
        if 'Item' not in response:
            return "⚠️ Task not found"

        task = response['Item']

        # Only penalize if task was not completed
        if task.get('status') != 'done':
            penalty = penalize_xp(user_id, 'delete')
            xp_lost = penalty.get('xp_lost', 0)
            total_xp = penalty.get('total_xp', 0)
        else:
            xp_lost = 0
            total_xp = None

        # Delete the task
        tasks_table.delete_item(Key={'userId': user_id, 'taskId': task_id})

        if xp_lost > 0:
            return f"🗑️ Task deleted\n\n⚠️ -{xp_lost} XP penalty\n\n💎 Total XP: {total_xp}"
        else:
            return "🗑️ Task deleted"

    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return "⚠️ Error deleting task"


def handle_snooze(user_id: int, task_id: str, delay: str) -> str:
    """Snooze task"""
    try:
        new_timestamp = parse_snooze_delay(delay)
        tasks_table.update_item(
            Key={'userId': user_id, 'taskId': task_id},
            UpdateExpression='SET remindAt = :new_time',
            ExpressionAttributeValues={':new_time': Decimal(str(new_timestamp))}
        )
        new_dt = datetime.fromtimestamp(new_timestamp)
        return f"⏰ Task snoozed!\nNew time: {new_dt.strftime('%d.%m.%Y в %H:%M')}"
    except Exception as e:
        logger.error(f"Error snoozing: {e}")
        return "❌ Error. Use: /snooze <id> <delay>\nExample: /snooze abc123 1h"


def handle_tags_list(user_id: int) -> str:
    """List all user tags"""
    try:
        response = tasks_table.query(
            KeyConditionExpression='userId = :uid',
            FilterExpression='#status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':uid': user_id, ':status': 'pending'}
        )

        all_tags = set()
        for task in response.get('Items', []):
            all_tags.update(task.get('tags', []))

        if not all_tags:
            return "🏷️ No tags yet.\nAdd #tag in task text!"

        tags_list = ' '.join(f'#{tag}' for tag in sorted(all_tags))
        return f"🏷️ Your tags:\n{tags_list}\n\nUse: /tasks #tag"
    except Exception as e:
        logger.error(f"Error listing tags: {e}")
        return "❌ Error"


def handle_stats(user_id: int) -> str:
    """Show user statistics (Phase 2)"""
    try:
        # Get all tasks
        response = tasks_table.query(KeyConditionExpression='userId = :uid',
                                     ExpressionAttributeValues={':uid': user_id})

        all_tasks = response.get('Items', [])
        completed = [t for t in all_tasks if t['status'] == 'done']
        pending = [t for t in all_tasks if t['status'] == 'pending']

        # This week
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_completed = [t for t in completed
                         if datetime.fromtimestamp(int(t.get('completedAt', 0))) > week_ago]

        # By tags
        tag_counts = {}
        for task in completed:
            for tag in task.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        tags_str = '\n'.join(f"#{tag}: {count}" for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:5])

        return (
            f"📊 **Your Statistics**\n\n"
            f"✅ Total completed: {len(completed)}\n"
            f"⏳ Pending: {len(pending)}\n"
            f"📈 This week: {len(week_completed)}\n\n"
            f"**Top tags:**\n{tags_str if tags_str else 'No tags yet'}\n\n"
            f"Keep it up! 💪"
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return "❌ Error getting statistics"


def handle_ai_analyze(user_id: int, task_text: str) -> str:
    """AI analysis of task"""
    try:
        result = call_ai_processor('analyze_task', {'taskText': task_text})

        if not result:
            return "❌ AI unavailable. Try again later."

        tags = result.get('suggestedTags', [])
        priority = result.get('suggestedPriority', 'medium')
        duration = result.get('estimatedDuration', 30)
        analysis = result.get('analysis', '')

        tags_str = ' '.join(f'#{t}' for t in tags) if tags else 'no tags'
        priority_emoji = get_priority_emoji(priority)

        return (
            f"🤖 **AI Analysis**\n\n"
            f"**Task:** {task_text}\n\n"
            f"**Priority:** {priority_emoji} {priority}\n"
            f"**Tags:** {tags_str}\n"
            f"**Est. Duration:** {duration} min\n\n"
            f"**Insight:** {analysis}\n\n"
            f"Use `/urgent {task_text}` to create with high priority"
        )
    except Exception as e:
        logger.error(f"Error in AI analyze: {e}")
        return "❌ AI error"


def handle_create_task(user_id: int, text: str, priority: str = 'medium') -> str:

    """Create task with tags and priority"""
    import uuid

    try:
        tags = parse_tags(text)
        parsed_dt = parse_smart_time(text)

        if not parsed_dt or parsed_dt < datetime.utcnow():
            return (
                "⚠️ Please specify time\n\n"
                "🕐 Examples:\n"
                "• \"Meeting in 2 hours #work\"\n"
                "• \"Buy milk Friday 18:00\"\n"
                "• \"Call dentist tomorrow 14:00\""
            )

        task_id = str(uuid.uuid4())
        remind_at = int(parsed_dt.timestamp())

        # Create task item
        task_item = {
            'userId': user_id,
            'taskId': task_id,
            'text': text,
            'remindAt': remind_at,
            'status': 'pending',
            'createdAt': int(datetime.utcnow().timestamp()),
            'priority': priority,
            'tags': tags if tags else [],
            'notified': False
        }

        # Save to DynamoDB
        tasks_table.put_item(Item=task_item)

        # NEW: Schedule reminder via EventBridge
        schedule_reminder(user_id, task_id, remind_at)

        # Send confirmation with task details
        priority_emoji = get_priority_emoji(priority)
        tags_str = ' ' + ' '.join(f'#{t}' for t in tags) if tags else ''

        return (
            f"✅ Task created!\n\n"
            f"{priority_emoji} **{text}**{tags_str}\n"
            f"⏰ {parsed_dt.strftime('%d.%m.%Y at %H:%M')}\n\n"
            f"ID: {task_id[:8]}"
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return "❌ Error creating task"


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {})
        user_id = message.get('from', {}).get('id')
        text = message.get('text', '')

        if not user_id or not text:
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}

        # Route commands
        if text.startswith('/start'):
            response = handle_start(user_id)
        elif text.startswith('/help'):
            response = handle_help(user_id)
        elif text.startswith('/app'):
            app_data = handle_app(user_id)
            send_telegram_message(user_id, app_data['text'], app_data.get('keyboard'))
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        elif text.startswith('/tasks'):
            parts = text.split()
            filter_tag = parts[1] if len(parts) > 1 and parts[1].startswith('#') else None
            response = handle_tasks_list(user_id, filter_tag)
        elif text.startswith('/done'):
            task_id = text.replace('/done', '').strip()
            response = handle_done(user_id, task_id)
        elif text.startswith('/urgent'):
            task_text = text.replace('/urgent', '').strip()
            response = handle_create_task(user_id, task_text, priority='high')
        elif text.startswith('/snooze'):
            parts = text.split()
            if len(parts) >= 3:
                task_id = parts[1]
                delay = parts[2]
                response = handle_snooze(user_id, task_id, delay)
            else:
                response = "Usage: /snooze <task_id> <delay>\nExample: /snooze abc123 1h"
        elif text.startswith('/delete'):
            task_id = text.replace('/delete', '').strip()
            if task_id:
                response = handle_delete_task(user_id, task_id)
            else:
                response = "Usage: /delete <task_id>\nExample: /delete abc123"
        elif text.startswith('/tags'):
            response = handle_tags_list(user_id)
        elif text.startswith('/stats'):
            response = handle_stats(user_id)
        elif text.startswith('/profile'):
            response = handle_profile(user_id)
        elif text.startswith('/ai'):
            task_text = text.replace('/ai', '').strip()
            if task_text:
                response = handle_ai_analyze(user_id, task_text)
            else:
                response = "Usage: /ai <task description>\nExample: /ai Prepare presentation for Monday"
        else:
            response = handle_create_task(user_id, text)

        send_telegram_message(user_id, response)

        return {'statusCode': 200, 'body': json.dumps({'ok': True})}


    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}", exc_info=True)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
