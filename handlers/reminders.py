from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards.reminders_kb import get_reminders_submenu_kb
from keyboards.main_menu import get_main_kb
from handlers.states import RemindStates

router = Router()

# Функция, которую вызывает планировщик
async def send_reminder(bot, user_id, text):
    await bot.send_message(user_id, f"🔔 <b>ВРЕМЯ ПРИШЛО!</b>\n\n📍 {text}")

# 1. Вход в подменю напоминаний
@router.message(F.text == "⏰ Напоминания")
async def show_reminders_menu(message: types.Message):
    await message.answer(
        "Управление напоминаниями. Выберите действие:",
        reply_markup=get_reminders_submenu_kb()
    )

# 2. Показ списка текущих задач в планировщике
@router.message(F.text == "📋 Мои задачи")
async def list_reminders(message: types.Message, scheduler: AsyncIOScheduler):
    jobs = scheduler.get_jobs()
    if not jobs:
        await message.answer("У вас пока нет активных напоминаний.")
        return

    text = "⏳ <b>Ближайшие события:</b>\n\n"
    for job in jobs:
        # Убираем системные задачи типа daily_report
        if job.func == send_reminder:
            # args[2] — это текст напоминания, который мы передали в планировщик
            text += f"🔹 {job.next_run_time.strftime('%H:%M')} — {job.args[2]}\n"
    
    await message.answer(text, parse_mode="HTML")

# 3. Начало процесса добавления
@router.message(F.text == "➕ Новое напоминание")
async def start_add_remind(message: types.Message, state: FSMContext):
    await state.set_state(RemindStates.waiting_for_text)
    await message.answer("О чем мне тебе напомнить? (Напиши текст)")

@router.message(RemindStates.waiting_for_text)
async def process_remind_text(message: types.Message, state: FSMContext):
    await state.update_data(remind_text=message.text)
    await state.set_state(RemindStates.waiting_for_time)
    await message.answer("Через сколько минут напомнить? (Напиши только число)")

@router.message(RemindStates.waiting_for_time)
async def process_remind_time(message: types.Message, state: FSMContext, scheduler: AsyncIOScheduler, bot):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи только цифры (количество минут).")
        return

    minutes = int(message.text)
    data = await state.get_data()
    text = data['remind_text']
    
    # Считаем время
    run_time = datetime.now() + timedelta(minutes=minutes)

    # Добавляем в APScheduler
    scheduler.add_job(
        send_reminder, 
        trigger='date', 
        run_date=run_time, 
        args=[bot, message.from_user.id, text]
    )

    await state.clear()
    await message.answer(
        f"✅ Принято! Напомню через {minutes} мин. о: <i>{text}</i>", 
        reply_markup=get_reminders_submenu_kb()
    )

# 4. Кнопка Назад
@router.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    await message.answer("Возвращаемся в главное меню", reply_markup=get_main_kb())