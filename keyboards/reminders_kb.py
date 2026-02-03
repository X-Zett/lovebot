from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_reminders_submenu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Новое напоминание")
    kb.button(text="📋 Мои задачи")
    kb.button(text="🔙 Назад")
    kb.adjust(2) 
    return kb.as_markup(resize_keyboard=True)