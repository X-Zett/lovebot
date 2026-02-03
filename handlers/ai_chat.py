from aiogram import Router, types, F
from aiogram.filters import Command
from utils.gemini_client import ask_gemini

router = Router()

@router.message(Command("ai"))
async def generic_ai_chat(message: types.Message):
    # Убираем команду /ai из текста
    user_text = message.text.replace("/ai", "").strip()
    
    if not user_text:
        await message.answer("Напиши что-нибудь после команды /ai, и я отвечу!")
        return

    # Здесь системная настройка уже другая — просто "полезный помощник"
    response = await ask_gemini(user_text, system_instruction="")
    await message.answer(response)