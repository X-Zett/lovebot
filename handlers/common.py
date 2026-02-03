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

@router.message(Command("revoke"))
async def revoke_access(message: types.Message):
    # Только главный админ может отзывать доступ
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return

    try:
        # Команда вида: /revoke 12345678
        parts = message.text.split()
        user_id_to_remove = int(parts[1])
        
        # Удаляем пользователя из таблицы
        await execute_query("DELETE FROM authorized_users WHERE user_id = ?", (user_id_to_remove,))
        await message.answer(f"🚫 Доступ для ID {user_id_to_remove} аннулирован.")
    except (IndexError, ValueError):
        await message.answer("Ошибка! Пиши: /revoke ID_пользователя")

@router.message(Command("users"))
async def list_authorized_users(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return

    from database.db import fetch_all
    rows = await fetch_all("SELECT user_id, name FROM authorized_users")
    
    if rows:
        text = "👥 <b>Разрешенные пользователи:</b>\n\n"
        for row in rows:
            text += f"• {row['name']} (<code>{row['user_id']}</code>)\n"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("Список пуст (кроме главного админа).")