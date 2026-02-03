from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import get_main_kb
from database.db import execute_query
import os

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        "Я твой домашний помощник. Используй кнопки ниже для навигации.",
        reply_markup=get_main_kb()
    )

@router.message(Command("grant"))
async def grant_access(message: types.Message):
    # Проверка: только "Главный Админ" из .env может давать доступ
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return

    try:
        # Команда вида: /grant 12345678 Имя
        parts = message.text.split()
        new_id = int(parts[1])
        name = parts[2] if len(parts) > 2 else "User"
        
        await execute_query("INSERT OR IGNORE INTO authorized_users (user_id, name) VALUES (?, ?)", (new_id, name))
        await message.answer(f"✅ Доступ для {name} (ID: {new_id}) открыт!")
    except:
        await message.answer("Ошибка! Пиши: /grant ID Имя")