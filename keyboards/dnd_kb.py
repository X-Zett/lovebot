from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_dnd_actions_kb(actions: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for action in actions:
        kb.button(text=action)
    kb.adjust(2) # Размещаем по 2 кнопки в ряд
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True) # one_time_keyboard=True - чтобы кнопки скрывались после выбора
                                                                     # но для D&D лучше без нее, чтобы кнопки всегда были