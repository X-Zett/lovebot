from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_riddle_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💡 Узнать разгадку", callback_data="show_answer")],
        [InlineKeyboardButton(text="🎲 Еще одна", callback_data="next_riddle")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)