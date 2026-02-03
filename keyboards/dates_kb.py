from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_dates_submenu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Добавить дату")
    kb.button(text="❌ Удалить дату")
    kb.button(text="🔙 Назад")
    kb.adjust(2) # Две кнопки в ряд, а "Назад" будет ниже
    return kb.as_markup(resize_keyboard=True)