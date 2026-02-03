from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db import is_user_authorized
import os

class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # 1. Проверяем, есть ли пользователь в базе
        authorized = await is_user_authorized(event.from_user.id)
        
        # 2. Даем доступ, если он в базе ИЛИ если это "Главный Админ" из .env
        admin_id = int(os.getenv("ADMIN_ID", 0))
        
        if authorized or event.from_user.id == admin_id:
            return await handler(event, data)
        
        # 3. Если чужой — вежливо (или не очень) отказываем
        await event.answer("⚠️ Доступ заблокирован. Ваш ID не найден в белом списке.")
        return