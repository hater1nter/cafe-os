from fastapi import APIRouter, Request, HTTPException
from aiogram import types
import structlog
import json

from app.telegram_bot.handlers import dp, bot, setup_bot
from app.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/telegram")

# Store setup status
_bot_setup_done = False


@router.on_event("startup")
async def startup():
    """Setup bot on startup"""
    global _bot_setup_done
    if not _bot_setup_done and settings.telegram_bot_token:
        await setup_bot()
        _bot_setup_done = True
        logger.info("telegram_bot_initialized")


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram bot webhook handler"""
    try:
        update_data = await request.json()
        update = types.Update(**update_data)

        # Process update with dispatcher
        await dp.feed_update(bot, update)

        logger.debug("telegram_update_processed", update_id=update.update_id)
        return {"status": "ok"}
    except Exception as e:
        logger.error("telegram_webhook_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bot/info")
async def get_bot_info():
    """Get bot information"""
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Bot token not configured")

    me = await bot.get_me()
    return {
        "bot_id": me.id,
        "bot_username": me.username,
        "bot_first_name": me.first_name,
        "is_bot": me.is_bot
    }


@router.post("/bot/set-webhook")
async def set_webhook(webhook_url: str):
    """Set webhook URL for Telegram bot"""
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Bot token not configured")

    try:
        await bot.set_webhook_url(webhook_url)
        logger.info("webhook_set", webhook_url=webhook_url)
        return {"status": "webhook_set", "url": webhook_url}
    except Exception as e:
        logger.error("webhook_set_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot/webhook-info")
async def get_webhook_info():
    """Get current webhook info"""
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Bot token not configured")

    info = await bot.get_webhook_info()
    return {
        "url": info.url,
        "has_custom_certificate": info.has_custom_certificate,
        "pending_update_count": info.pending_update_count,
        "ip_address": info.ip_address,
        "last_error_date": info.last_error_date,
        "last_error_message": info.last_error_message
    }
