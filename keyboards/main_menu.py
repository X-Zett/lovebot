from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    # Добавляем кнопки
    kb.button(text="📸 Случайное фото")
    kb.button(text="🗓 Важные даты")
    kb.button(text="⏰ Напоминания")
    kb.button(text="💰 Мой бюджет")
    kb.button(text="🤫 Желание")
    kb.button(text="🎲 Что выбрать?")
    
    # Настраиваем сетку: по 2 кнопки в ряд
    kb.adjust(2)
    
    # resize_keyboard=True делает кнопки компактными (не на пол-экрана)
    return kb.as_markup(resize_keyboard=True)