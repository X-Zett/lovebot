from aiogram.fsm.state import StatesGroup, State

class DateStates(StatesGroup):
    waiting_for_date_text = State() # Состояние ожидания текста даты
    waiting_for_delete_id = State() # Состояние ожидания ID для удаления