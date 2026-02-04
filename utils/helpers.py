from aiogram import types

async def answer_with_loading(message: types.Message, task_func, loading_text="🔮 <i>Думаю...</i>", **kwargs):
    """
    Универсальная функция: шлет текст загрузки, ждет задачу и редактирует сообщение.
    """
    temp_msg = await message.answer(loading_text, parse_mode="HTML")
    try:
        # Выполняем запрос к ИИ
        result = await task_func(**kwargs)
        # Редактируем временное сообщение результатом
        return await temp_msg.edit_text(result, parse_mode="HTML")
    except Exception as e:
        return await temp_msg.edit_text(f"❌ Ошибка: {e}")