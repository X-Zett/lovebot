from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_dnd_actions_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Вариант A"))
    kb.add(KeyboardButton(text="Вариант B"))
    kb.add(KeyboardButton(text="Вариант C"))
    kb.add(KeyboardButton(text="Вариант D"))
    kb.add(KeyboardButton(text="✍️ Свой вариант"))
    kb.add(KeyboardButton(text="📊 Статус"))
    kb.add(KeyboardButton(text="❌ Завершить игру")) # Новая кнопка
    
    kb.adjust(2, 2, 2, 1) 
    return kb.as_markup(resize_keyboard=True)