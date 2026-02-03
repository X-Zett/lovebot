from aiogram import Router, types, F
from database.db import execute_query

router = Router()

@router.callback_query(F.data == "save_meme")
async def save_to_favorites(callback: types.CallbackQuery):
    # Достаем заголовок и ссылку
    title = callback.message.caption.replace("🤣 Мем часа:\n", "").replace("🤣 Мем по запросу:\n", "").replace("⭐ Из вашей коллекции:\n", "")
    
    # Сохраняем file_id самой крупной версии фото
    file_id = callback.message.photo[-1].file_id
    
    await execute_query(
        "INSERT OR IGNORE INTO favorite_memes (user_id, url, title) VALUES (?, ?, ?)",
        (callback.from_user.id, file_id, title)
    )
    
    await callback.answer("✅ Добавлено в коллекцию!")

@router.callback_query(F.data == "delete_meme_msg")
async def delete_meme_completely(callback: types.CallbackQuery):
    # Получаем ID файла
    file_id = callback.message.photo[-1].file_id
    
    # 1. Удаляем из базы данных (если он там был)
    await execute_query(
        "DELETE FROM favorite_memes WHERE user_id = ? AND url = ?",
        (callback.from_user.id, file_id)
    )
    
    # 2. Удаляем само сообщение из чата
    try:
        await callback.message.delete()
        await callback.answer("🗑 Удалено из чата и коллекции")
    except Exception:
        # Если сообщение старое и его нельзя удалить, просто пришлем уведомление
        await callback.answer("❌ Не удалось удалить сообщение, но из коллекции убрано.")