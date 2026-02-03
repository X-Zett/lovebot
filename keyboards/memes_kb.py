from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_memes_submenu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎲 Рассмеши меня")
    kb.button(text="❤️ Моя коллекция")
    kb.button(text="🔙 Назад")
    kb.adjust(2) 
    return kb.as_markup(resize_keyboard=True)