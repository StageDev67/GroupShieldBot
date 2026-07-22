import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from bot.database.db_manager import db
from bot.handlers import setup_handlers

# Создаем бота и диспетчер
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ============ ЗАПУСК ============
async def main():
    logging.basicConfig(level=logging.INFO)
    await db.init_db()
    setup_handlers(dp)
    print("🚀 БОТ ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())