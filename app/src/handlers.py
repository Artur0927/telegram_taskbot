"""
Telegram message handlers using Aiogram.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message

from .ai_engine import generate_response

logger = logging.getLogger(__name__)
router = Router(name="main_handlers")


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """Handle all text messages."""
    user_text = message.text
    user_id = message.from_user.id if message.from_user else "unknown"
    
    logger.info(f"Message from {user_id}: {user_text[:50]}...")
    
    # Send thinking indicator
    thinking = await message.answer("🤔 Thinking...")
    
    try:
        # Generate response
        response = await generate_response(user_text)
        
        # Edit thinking message with response
        if len(response) > 4000:
            await thinking.delete()
            for i in range(0, len(response), 4000):
                await message.answer(response[i:i+4000])
        else:
            await thinking.edit_text(response)
            
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await thinking.edit_text("❌ Sorry, something went wrong.")


@router.message()
async def handle_other(message: Message) -> None:
    """Handle non-text messages."""
    await message.answer(
        "👋 Hi! Send me a text message and I'll respond using AI.\n\n"
        "Powered by Google Gemini 🤖"
    )
