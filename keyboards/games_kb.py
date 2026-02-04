from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_riddle_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💡 Узнать разгадку", callback_data="show_answer")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)