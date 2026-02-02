from aiogram import Router, types, F
from aiogram.filters import Command
from database.db import execute_query, fetch_one

router = Router()

@router.message(F.photo)
async def save_memory(message: types.Message):
    await execute_query('INSERT INTO memories (file_id) VALUES (?)', (message.photo[-1].file_id,))
    await message.reply("📸 Сохранил в локальную базу!")

@router.message(Command("random_memory"))
async def get_memory(message: types.Message):
    row = await fetch_one('SELECT file_id FROM memories ORDER BY RANDOM() LIMIT 1')
    if row:
        await message.answer_photo(row['file_id'], caption="Помнишь это? ❤️")
    else:
        await message.answer("Копилка пуста.")