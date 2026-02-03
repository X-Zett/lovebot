from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db import is_user_authorized
import os

GROUP_ID = int(os.getenv("GROUP_ID", 0))

class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Разрешаем, если это личка и пользователь в списке
        is_authorized = await is_user_authorized(event.from_user.id)
        is_admin = event.from_user.id == int(os.getenv("ADMIN_ID", 0))
        
        # РАЗРЕШАЕМ, если сообщение пришло из вашей конкретной группы
        is_target_group = event.chat.id == GROUP_ID
        
        if is_authorized or is_admin or is_target_group:
            return await handler(event, data)
        
        return # Игнорируем остальных