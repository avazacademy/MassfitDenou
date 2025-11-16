import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers import start
from app.handlers.admin import router as admin_router
from app.handlers.user import router as user_router
from app.config import BOT_TOKEN
from app.database.models import Base
from app.database.engine import engine


async def on_startup():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables created successfully")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    await on_startup()
    
    # Initialize bot with default properties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # Drop pending updates to avoid flooding when bot restarts
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    logging.info("Bot started successfully")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
