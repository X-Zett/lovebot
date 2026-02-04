from aiogram import Router, types, F
from aiogram.filters import Command
from utils.gemini_client import ask_gemini
from keyboards.games_kb import get_riddle_kb

router = Router()

# Системная настройка для игры
# DANETKA_SYSTEM = (
#     "Ты — ведущий игры 'Абсурдная Данетка'. Твой юмор глупый но смешной."
#     "Твоя цель — выдаешь начало странной истории, которая имеет логичную разгадку, а игроки должны найти ответ/разгадать. Ограничивайся несколькими предложениями, без лишних вступлений, только ситуация и вопрос."
# )

# @router.message(Command("danetka"))
# async def play_danetka(message: types.Message):
#     temp_msg = await message.answer("🔮 <i>Связываюсь с астралом (создаю ситуацию)...</i>", parse_mode="HTML")

#     prompt = "Придумай новую глупую и смешную ситуацию для данетки."
#     situation = await ask_gemini(prompt, system_instruction=DANETKA_SYSTEM)
    
#     await temp_msg.edit_text(
#         f"🤔 <b>Данетка от ИИ:</b>\n\n{situation}",
#         reply_markup=get_riddle_kb(),
#         parse_mode="HTML"
#     )

# @router.callback_query(F.data == "show_answer")
# async def show_danetka_answer(callback: types.CallbackQuery):
#     situation = callback.message.text
#     prompt = f"Придумай максимально глупую но смешную разгадку для этой ситуации: {situation}"
#     answer = await ask_gemini(prompt, system_instruction=DANETKA_SYSTEM)
    
#     await callback.message.edit_text(
#         f"{situation}\n\n✨ <b>Разгадка:</b> {answer}",
#         reply_markup=get_riddle_kb()
#     )