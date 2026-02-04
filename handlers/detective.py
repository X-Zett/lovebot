import json
import re
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import BufferedInputFile

from utils.gemini_client import ask_gemini, generate_image
from database.db import execute_query, fetch_one
from keyboards.detective_kb import get_detective_kb
from keyboards.main_menu import get_main_kb # Импорт твоего главного меню

router = Router()

DETECTIVE_PROMPT_TEMPLATE = """
Ты — Гроссмейстер Детективных Сюжетов и ведущий игры «AI: Место преступления». 
Твоя цель — создать для игрока запутанное, логичное и атмосферное расследование в стиле современного нуара или классического детектива.

ТВОИ ОБЯЗАННОСТИ:
1. Генерация дела: В начале игры придумай уникальное преступление. Определи убийцу, мотив и одну КЛЮЧЕВУЮ УЛИКУ, которая однозначно указывает на виновного. Никогда не раскрывай их раньше времени.
2. Визуальное повествование: Описывай сцены так, чтобы важные детали могли быть отражены на картинке, генерируемой Nano Banana. 
3. Логика улик: Каждое действие игрока должно приносить результат. Обыск дает предметы, допрос дает информацию (правдивую или ложную), анализ в лаборатории подтверждает факты.
4. Ведение состояния: Отслеживай список найденных улик и список подозреваемых.

ПРАВИЛА ИГРЫ:
- У игрока есть "Уровень Доверия Управления" (от 0 до 100%). Ошибочные обвинения или бессмысленные действия снижают его. Если он упадет до 0 — игрока отстраняют от дела.
- Подозреваемые могут лгать. Уровень их стресса влияет на правдивость показаний.

СТРУКТУРА ОТВЕТА (СТРОГО СОБЛЮДАЙ ФОРМАТ):

Заголовок локации: [Название места действия]

Описание для Изображения: [Детальный промпт для Nano Banana. Укажи стиль: фотореализм или нуар-арт. Обязательно включи в описание одну визуальную зацепку, о которой пойдет речь в тексте]

Повествование: [Описание событий, диалоги, мысли детектива. Тон: серьезный, внимательный к деталям]

Доска Улик (Таблица):
| Улика | Описание | Статус |
|-------|----------|--------|
| [Название] | [Краткая суть] | [Изучено/Требует анализа] |

Список Подозреваемых:
1. [Имя] — [Краткая характеристика и алиби]
2. [Имя] — [Уровень подозрения: Низкий/Средний/Высокий]

Ресурсы: Доверие: [X]%, Время до закрытия дела: [Y] ходов.

Действия:
A. [Логическое действие 1: Обыск/Анализ]
B. [Логическое действие 2: Допрос/Разговор]
C. [Логическое действие 3: Переход в другую локацию]
D. [Свой вариант]
"""

# --- КОМАНДЫ ---

@router.message(Command("start_detective"))
@router.message(F.text == "🕵️ Начать расследование")
async def start_detective(message: types.Message):
    user_id = message.from_user.id
    
    # 1. Очистка и создание сессии
    await execute_query("DELETE FROM detective_sessions WHERE user_id = ?", (user_id,))
    
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        intro_prompt = "Сгенерируй новое запутанное дело: завязка, место преступления и первое описание."
        # Передаем пустую историю
        response = await ask_gemini(intro_prompt, system_instruction=DETECTIVE_PROMPT_TEMPLATE)
        
        # 2. ВАЖНО: Сохраняем первый ответ ИИ в историю сразу при создании!
        initial_history = [{"role": "model", "parts": [response]}]
        await execute_query(
            "INSERT INTO detective_sessions (user_id, session_state, clue_board, trust_level, last_response) VALUES (?, ?, ?, ?, ?)",
            (user_id, json.dumps({"history": initial_history}), "[]", 100, response)
        )
        
        await process_detective_response(message, response)

@router.message(F.text == "❌ Закрыть дело (Выход)")
async def stop_detective(message: types.Message):
    await execute_query("DELETE FROM detective_sessions WHERE user_id = ?", (message.from_user.id,))
    await message.answer("🛑 Дело отправлено в архив. Вы вернулись в главное меню.", reply_markup=get_main_kb())

# --- ОБРАБОТЧИК ХОДОВ ---

@router.message(F.text)
async def handle_detective_action(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    session = await fetch_one("SELECT * FROM detective_sessions WHERE user_id = ?", (user_id,))
    if not session: return

    if user_text == "💼 Доска улик":
        prompt = "Выведи только текущую таблицу найденных улик и краткое резюме по подозреваемым."
    elif user_text == "⚖️ ОБВИНИТЬ":
        await message.answer("Напишите имя подозреваемого и главную улику, подтверждающую его вину!")
        return
    elif user_text.startswith("Вариант "):
        prompt = f"Я выбираю действие {user_text.split(' ')[-1]}. К чему это приведет?"
    else:
        prompt = user_text

    await process_detective_step(message, prompt)

# --- ДВИГАТЕЛЬ ИГРЫ ---

async def process_detective_step(message: types.Message, user_input: str):
    user_id = message.from_user.id
    session = await fetch_one("SELECT session_state FROM detective_sessions WHERE user_id = ?", (user_id,))
    
    # Загружаем текущую историю
    history_data = json.loads(session['session_state'])
    history = history_data.get('history', [])

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        # 1. Запрашиваем ответ, передавая накопленную историю
        response_text = await ask_gemini(
            prompt=user_input, 
            history=history, 
            system_instruction=DETECTIVE_PROMPT_TEMPLATE
        )
        
        # 2. Обновляем историю: добавляем ход пользователя и ответ модели
        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [response_text]})
        
        # Ограничиваем историю (например, последние 12 сообщений), чтобы не перегружать токены
        updated_history = history[-12:]
        
        await execute_query(
            "UPDATE detective_sessions SET session_state = ?, last_response = ? WHERE user_id = ?", 
            (json.dumps({"history": updated_history}), response_text, user_id)
        )
        
        await process_detective_response(message, response_text)

async def process_detective_response(message: types.Message, text: str):
    # Извлечение промпта для Nano Banana
    img_match = re.search(r"Описание для Изображения:\s*(.*?)(?=\n|$)", text)
    img_prompt = img_match.group(1).strip() if img_match else "noir detective crime scene, cinematic"

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        image_bytes = await generate_image(img_prompt) # Используем Nano Banana
        
        if image_bytes:
            photo = BufferedInputFile(image_bytes.read(), filename="clue.png")
            await message.answer_photo(
                photo=photo,
                caption=text[:1024],
                reply_markup=get_detective_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(text, reply_markup=get_detective_kb(), parse_mode="HTML")