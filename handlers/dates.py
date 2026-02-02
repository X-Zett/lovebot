from aiogram import Router, types, F  # <--- Добавь F здесь
from aiogram.filters import Command
from database.db import execute_query, fetch_all

router = Router()

# Теперь функция сработает И на команду, И на текст с кнопки
@router.message(F.text == "🗓 Важные даты") # <--- Добавили реакцию на кнопку
@router.message(Command("dates"))
async def show_dates(message: types.Message):
    rows = await fetch_all('SELECT info FROM important_dates')
    
    if rows:
        text = "🗓 <b>Важные даты:</b>\n\n"
        for row in rows:
            text += f"▪️ {row['info']}\n"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("Список дат пока пуст. Добавь что-нибудь через /add_date")

@router.message(Command("add_date"))
async def add_date(message: types.Message):
    date_info = message.text.replace("/add_date", "").strip()
    
    if not date_info:
        await message.answer("Пример использования:\n<code>/add_date 19 октября — Начало любви</code>", parse_mode="HTML")
        return

    await execute_query('INSERT INTO important_dates (info) VALUES (?)', (date_info,))
    await message.answer("✅ Дата успешно сохранена!")