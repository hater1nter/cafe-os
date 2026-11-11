import asyncio
import logging
from app.telegram_bot.handlers import dp, bot, set_bot_commands
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Start the bot"""
    logger.info("Starting Telegram bot...")
    await set_bot_commands()

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
