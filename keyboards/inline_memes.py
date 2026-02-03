from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_meme_actions_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="❤️ В коллекцию", callback_data="save_meme"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_meme_msg")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)