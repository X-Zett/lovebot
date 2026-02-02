import asyncio
import logging
from aiogram import Bot, Dispatcher
from database.db import init_db
from dotenv import load_dotenv
from handlers import memories, other, dates, common
import os

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # Запуск базы
    await init_db()

    # Подключаем части бота
    dp.include_router(common.router) # Лучше регистрировать первым
    dp.include_router(memories.router)
    dp.include_router(other.router)
    dp.include_router(dates.router)

    print("🚀 Бот запущен локально на SQLite!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())