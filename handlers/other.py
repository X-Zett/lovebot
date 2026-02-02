import random
from aiogram import Router, types
from aiogram.filters import Command
from database.db import execute_query, fetch_val, fetch_one

router = Router()

@router.message(Command("spend"))
async def add_expense(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        await execute_query('INSERT INTO expenses (amount) VALUES (?)', (amount,))
        total = await fetch_val('SELECT SUM(amount) FROM expenses')
        await message.answer(f"💰 Записал {amount}. Итого потрачено: {total}")
    except:
        await message.answer("Пиши: /spend 500")

@router.message(Command("wish"))
async def add_wish(message: types.Message):
    wish_text = message.text.replace("/wish", "").strip()
    if wish_text:
        await execute_query('INSERT INTO wishes (user_id, text) VALUES (?, ?)', 
                            (message.from_user.id, wish_text))
        await message.answer("🤫 Секрет сохранен в SQLite!")

@router.message(Command("choose"))
async def choose_random(message: types.Message):
    options = message.text.replace("/choose", "").split(",")
    if len(options) > 1:
        await message.answer(f"🎲 Судьба выбрала: {random.choice(options).strip()}")