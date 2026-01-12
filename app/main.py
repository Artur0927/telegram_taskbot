"""
Main application - FastAPI server with Telegram webhook.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request, Response

from src.config import config
from src.handlers import router as message_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Validate config
config.validate()

# Initialize Bot and Dispatcher
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(message_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Try to set webhook (may fail without HTTPS)
    webhook_url = f"{config.WEBHOOK_URL}/webhook"
    logger.info(f"Setting webhook: {webhook_url}")
    
    try:
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")
    except Exception as e:
        logger.warning(f"Webhook setup failed (HTTPS required): {e}")
        logger.info("Bot will still respond to direct /webhook POST requests")
    
    yield
    
    # Shutdown: Delete webhook
    logger.info("Deleting webhook...")
    try:
        await bot.delete_webhook()
    except Exception:
        pass
    await bot.session.close()


# FastAPI app
app = FastAPI(
    title="Telegram Bot",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint for ALB."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"service": "telegram-bot", "status": "running"}


@app.post("/webhook")
async def webhook(request: Request) -> Response:
    """Process Telegram webhook updates."""
    try:
        update = Update.model_validate(await request.json())
        await dp.feed_update(bot=bot, update=update)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=200)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )
