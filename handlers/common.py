from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import get_main_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        "Я твой домашний помощник. Используй кнопки ниже для навигации.",
        reply_markup=get_main_kb()
    )