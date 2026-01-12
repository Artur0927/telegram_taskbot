"""
Telegram message handlers using Aiogram.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from src import ai_engine, job_engine

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Hello! I am your 🤖 **Smart Job Assistant**.\n\n"
        "Tell me what you are looking for, e.g.:\n"
        "• _Find me a Python Developer job in Berlin_\n"
        "• _Remote Marketing jobs_\n\n"
        "Or just chat with me!",
        parse_mode="Markdown"
    )

@router.message(Command("jobs"))
async def cmd_jobs(message: Message):
    """Explicit job search command: /jobs role in location"""
    args = message.text.replace("/jobs", "").strip()
    if not args:
        await message.answer("Please specify a role. Example: `/jobs Python Developer`", parse_mode="Markdown")
        return

    # specific parsing if needed, but passing to AI extractor is smarter
    analysis = await ai_engine.extract_job_params(args)
    if analysis.get('role'):
        await message.answer(f"🔎 Searching for **{analysis['role']}** in **{analysis['location'] or 'any location'}**...", parse_mode="Markdown")
        result = await job_engine.search_jobs(analysis['role'], analysis['location'])
        await message.answer(result, parse_mode="Markdown")
    else:
        # Fallback simple search
        await message.answer(f"🔎 Searching for **{args}**...", parse_mode="Markdown")
        result = await job_engine.search_jobs(args)
        await message.answer(result, parse_mode="Markdown")

@router.message(F.text)
async def handle_message(message: Message):
    """Handle natural language messages"""
    user_text = message.text
    user_id = message.from_user.id if message.from_user else "unknown"
    
    logger.info(f"Message from {user_id}: {user_text[:50]}...")

    # 1. Analyze Intent
    intent = await ai_engine.extract_job_params(user_text)
    
    if intent.get("is_job_request"):
        # 2. It's a Job Search!
        role = intent.get("role")
        location = intent.get("location", "any location")
        
        if not role:
            await message.answer("I couldn't identify a job role. Please be more specific.")
            return

        await message.answer(f"🔎 Searching for **{role}** in **{location}**...", parse_mode="Markdown")
        result = await job_engine.search_jobs(role, location)
        await message.answer(result, parse_mode="Markdown")
    else:
        # 3. It's just chat
        # Send thinking indicator
        thinking = await message.answer("🤔 Thinking...")
        
        try:
            response = await ai_engine.generate_response(user_text)
            await thinking.edit_text(response)
            
        except Exception as e:
            logger.error(f"Handler error: {e}")
            await thinking.edit_text("❌ Sorry, something went wrong.")


@router.message()
async def handle_other(message: Message) -> None:
    """Handle non-text messages."""
    await message.answer(
        "👋 Hi! Send me a text message and I'll respond using AI."
    )
