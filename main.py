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
from handlers import memories, other, dates, common, reminders, inline, meme_actions

from middlewares.access import AccessMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from utils.memes import get_random_meme
from keyboards.inline_memes import get_meme_actions_kb

load_dotenv()

# Функция для ежедневного уведомления (тот самый "Дайджест")
async def daily_report(bot: Bot):
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        await bot.send_message(
            int(admin_id), 
            "☀️ <b>Доброе утро!</b>\nБот работает исправно, не забудь проверить важные даты!"
        )

async def send_hourly_meme(bot: Bot):
    # Проверяем текущий час (по времени сервера/ноутбука)
    current_hour = datetime.now().hour
    
    # "Тихий режим": работаем только с 9 до 23 включительно (00:00 — уже стоп)
    if 9 <= current_hour < 24:
        admin_id = os.getenv("ADMIN_ID")
        meme = await get_random_meme()
        
        if meme and admin_id:
            try:
                await bot.send_photo(
                    int(admin_id), 
                    photo=meme['url'], 
                    caption=f"🤣 Мем часа:\n{meme['title']}",
                    reply_markup=get_meme_actions_kb()
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке мема: {e}")
    else:
        logging.info(f"Тихий режим: сейчас {current_hour}:00, мем не отправлен.")

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
    scheduler.add_job(
        send_hourly_meme, 
        trigger='interval', 
        hours=1, 
        args=[bot]
    )    
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
    dp.include_router(reminders.router)
    dp.include_router(inline.router)
    dp.include_router(meme_actions.router)
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