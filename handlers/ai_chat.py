from aiogram import Router, types, F
from aiogram.filters import Command
from utils.gemini_client import ask_gemini
from utils.helpers import answer_with_loading

router = Router()

@router.message(Command("ai"))
async def generic_ai_chat(message: types.Message):
    # Убираем команду /ai из текста
    user_text = message.text.replace("/ai", "").strip()
    
    if not user_text:
        await message.answer("Напиши что-нибудь после команды /ai, и я отвечу!")
        return

    await answer_with_loading(
        message, 
        task_func=ask_gemini, 
        prompt=user_text, 
        system_instruction=""
    )