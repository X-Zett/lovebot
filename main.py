import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.db import init_db
from dotenv import load_dotenv

# Импортируем роутеры (не забудь добавить reminders)
from handlers import memories, other, dates, common, reminders

from middlewares.access import AccessMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

# Функция для ежедневного уведомления (тот самый "Дайджест")
async def daily_report(bot: Bot):
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        await bot.send_message(
            int(admin_id), 
            "☀️ <b>Доброе утро!</b>\nБот работает исправно, не забудь проверить важные даты!"
        )

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Инициализация бота с поддержкой HTML по умолчанию
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 1. Запуск планировщика (APScheduler)
    # Указываем временную зону твоего региона
    scheduler = AsyncIOScheduler(timezone="Asia/Almaty") 
    
    # Добавляем задачу: каждое утро в 09:00 (опционально)
    scheduler.add_job(daily_report, trigger='cron', hour=9, minute=0, args=[bot])
    
    # Стартуем планировщик
    scheduler.start()

    # 2. Инициализация базы данных
    await init_db()

    # 3. Регистрация Middleware (безопасность)
    dp.message.outer_middleware(AccessMiddleware())

    # 4. Подключение роутеров
    dp.include_router(common.router)
    dp.include_router(dates.router)
    dp.include_router(memories.router)
    dp.include_router(reminders.router) # Новый роутер для напоминаний
    dp.include_router(other.router)

    print("🚀 Бот успешно запущен на твоем Lenovo!")
    
    # 5. Запуск поллинга 
    # Передаем scheduler и bot в контекст, чтобы они были доступны в хендлерах
    try:
        await dp.start_polling(bot, scheduler=scheduler)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот выключен")