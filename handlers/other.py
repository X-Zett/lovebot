import random
from aiogram import Router, types, F
from aiogram.filters import Command
from database.db import execute_query, fetch_val, fetch_one
from utils.memes import get_random_meme
from keyboards.inline_memes import get_meme_actions_kb
from keyboards.memes_kb import get_memes_submenu_kb
from keyboards.main_menu import get_main_kb

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

@router.message(F.text == "🤡 Мемо-станция")
async def show_memes_menu(message: types.Message):
    await message.answer(
        "Добро пожаловать в Мемо-станцию! 🎭\nЗдесь можно зарядиться позитивом.",
        reply_markup=get_memes_submenu_kb()
    )

@router.message(F.text == "🎲 Рассмеши меня")
async def send_meme_on_demand(message: types.Message):
    meme = await get_random_meme()
    if meme:
        await message.answer_photo(
            photo=meme['url'], 
            caption = (
                f"✨ <b>{meme['sub']}</b>\n"
                f"───\n"
                f"🤣 {meme['title']}"
            ),
            reply_markup=get_meme_actions_kb()
        )
    else:
        await message.answer("Мемы закончились, приходи позже!")

# 3. Показать случайный мем из коллекции
@router.message(F.text == "❤️ Моя коллекция")
async def show_favorites(message: types.Message):
    # Берем случайный мем из сохраненных для этого пользователя
    row = await fetch_one(
        "SELECT url, title FROM favorite_memes WHERE user_id = ? ORDER BY RANDOM() LIMIT 1", 
        (message.from_user.id,)
    )
    
    if row:
        await message.answer_photo(
            photo=row['url'], 
            caption=f"⭐ Из вашей коллекции:\n{row['title']}",
            reply_markup=get_meme_actions_kb() # Добавим кнопки и сюда, если захочешь удалить
        )
    else:
        await message.answer("Ваша коллекция пока пуста. Нажимайте ❤️ под мемами, которые я присылаю!")

# 4. Возврат в главное меню
@router.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_kb())