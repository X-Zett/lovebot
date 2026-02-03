from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import execute_query, fetch_all
from keyboards.dates_kb import get_dates_submenu_kb
from keyboards.main_menu import get_main_kb # Для кнопки "Назад"
from handlers.states import DateStates

router = Router()

# 1. Показ списка и СМЕНА КЛАВИАТУРЫ
@router.message(F.text == "🗓 Важные даты")
@router.message(Command("dates"))
async def show_dates_menu(message: types.Message):
    rows = await fetch_all('SELECT id, info FROM important_dates')
    if rows:
        text = "🗓 <b>Важные даты:</b>\n\n"
        for row in rows:
            text += f"ID: {row['id']} | {row['info']}\n"
    else:
        text = "Список дат пока пуст."
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_dates_submenu_kb())

# 2. Вход в режим добавления
@router.message(F.text == "➕ Добавить дату")
async def start_add_date(message: types.Message, state: FSMContext):
    await state.set_state(DateStates.waiting_for_date_text)
    await message.answer("Введите описание даты (например: 1 января - Новый год):")

# 3. Сохранение введенной даты
@router.message(DateStates.waiting_for_date_text)
async def process_add_date(message: types.Message, state: FSMContext):
    await execute_query('INSERT INTO important_dates (info) VALUES (?)', (message.text,))
    await state.clear() # Выходим из режима ожидания
    await message.answer(f"✅ Сохранено: {message.text}", reply_markup=get_dates_submenu_kb())

# 4. Удаление (простой вариант по ID)
@router.message(F.text == "❌ Удалить дату")
async def start_delete_date(message: types.Message, state: FSMContext):
    await state.set_state(DateStates.waiting_for_delete_id)
    await message.answer("Введите ID даты, которую нужно удалить (номер перед датой):")

@router.message(DateStates.waiting_for_delete_id)
async def process_delete_date(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await execute_query('DELETE FROM important_dates WHERE id = ?', (int(message.text),))
        await state.clear()
        await message.answer("🗑 Дата удалена!", reply_markup=get_dates_submenu_kb())
    else:
        await message.answer("Пожалуйста, введите только число (ID).")

# 5. Возврат в главное меню
@router.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    await message.answer("Возвращаемся в главное меню", reply_markup=get_main_kb())