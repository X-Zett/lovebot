from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_detective_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    
    # Игровые действия
    kb.add(KeyboardButton(text="Вариант A"))
    kb.add(KeyboardButton(text="Вариант B"))
    kb.add(KeyboardButton(text="Вариант C"))
    kb.add(KeyboardButton(text="Вариант D"))
    
    # Управление делом
    kb.add(KeyboardButton(text="💼 Доска улик"))
    kb.add(KeyboardButton(text="✍️ Свой вариант / Обыск"))
    kb.add(KeyboardButton(text="⚖️ ОБВИНИТЬ"))
    kb.add(KeyboardButton(text="❌ Закрыть дело (Выход)"))
    
    kb.adjust(2, 2, 2, 2)
    return kb.as_markup(resize_keyboard=True)