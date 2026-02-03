import random
from aiogram import Router, types, F # Добавили F
from aiogram.filters import Command
from database.db import execute_query, fetch_val, fetch_one
from utils.memes import get_random_meme

router = Router()

# 1. Бюджет (реакция на кнопку и на команду)
@router.message(F.text == "💰 Мой бюджет")
@router.message(Command("spend"))
async def add_expense(message: types.Message):
    # Если в тексте есть число (например, "/spend 500"), записываем трату
    try:
        parts = message.text.split()
        if len(parts) > 1 and parts[1].isdigit():
            amount = int(parts[1])
            await execute_query('INSERT INTO expenses (amount) VALUES (?)', (amount,))
            total = await fetch_val('SELECT SUM(amount) FROM expenses')
            await message.answer(f"✅ Записал {amount}. Итого потрачено: {total}")
        else:
            # Если просто нажата кнопка или введена команда без числа
            total = await fetch_val('SELECT SUM(amount) FROM expenses')
            await message.answer(f"📊 Текущие расходы: {total}\n\nЧтобы добавить трату, напиши: <code>/spend 500</code>", parse_mode="HTML")
    except Exception:
        await message.answer("Ошибка! Пиши: /spend 500")

# 2. Желания (кнопка показывает случайное, команда добавляет)
@router.message(F.text == "🤫 Желание")
@router.message(Command("random_wish"))
async def get_random_wish(message: types.Message):
    row = await fetch_one('SELECT text FROM wishes ORDER BY RANDOM() LIMIT 1')
    if row:
        await message.answer(f"🎲 Случайное желание: {row['text']}")
    else:
        await message.answer("Список желаний пуст. Добавь через /wish текст")

@router.message(Command("wish"))
async def add_wish(message: types.Message):
    wish_text = message.text.replace("/wish", "").strip()
    if wish_text:
        await execute_query('INSERT INTO wishes (user_id, text) VALUES (?, ?)', 
                            (message.from_user.id, wish_text))
        await message.answer("🤫 Секрет сохранен в базу!")

# 3. Колесо выбора
@router.message(F.text == "🎲 Что выбрать?")
@router.message(Command("choose"))
async def choose_random(message: types.Message):
    options = message.text.replace("/choose", "").replace("🎲 Что выбрать?", "").split(",")
    if len(options) > 1:
        await message.answer(f"🎲 Судьба выбрала: {random.choice(options).strip()}")
    else:
        await message.answer("Напиши варианты через запятую, например:\n/choose Пицца, Роллы, Бургер")

@router.message(F.text == "🤡 Рассмеши меня")
async def send_meme_on_demand(message: types.Message):
    meme = await get_random_meme()
    if meme:
        await message.answer_photo(photo=meme['url'], caption=meme['title'])
    else:
        await message.answer("Прости, мемовая шахта временно пуста 😔")