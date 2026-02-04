import json
import re
import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from keyboards.main_menu import get_main_kb

from utils.gemini_client import ask_gemini, generate_image
from database.db import execute_query, fetch_one
from keyboards.dnd_kb import get_dnd_actions_kb

router = Router()

# Твой амбициозный промпт для Dungeon Master
DM_PROMPT_TEMPLATE = """
Ты — опытный и креативный Dungeon Master (DM) в уникальной кампании Dungeons & Dragons. 
Твоя задача — вести игру для 1-4 игроков в группе.
Сеттинг и Тон:
Мир: Живой, детализированный фэнтези-мир, где магия переплетается с бытовыми странностями. 
Сюжет должен быть глубоким и взаимосвязанным: к примеру, события в первой главе могут 
неожиданно аукнуться в финале и так далее.
Тон: Баланс между эпическим приключением и абсурдным юмором (в духе Терри Пратчетта 
или Baldur’s Gate 3). Могут встречаться нелепые монстры, странные проклятия и 
комичные NPC, но ставки в сюжете всегда высоки.

СТРУКТУРА ОТВЕТА (СОБЛЮДАЙ СТРОГО):
Заголовок локации: [Название]
Описание для Изображения: [Четкое описание сцены для генерации картинки]
Повествование: Описание происходящего, диалоги, описание запахов, звуков и действий
Статус Игроков (Таблица): [Таблица с HP и инвентарем]
Действия: 
A. [Вариант 1]
B. [Вариант 2]
C. [Вариант 3]
D. [Вариант 4]

Используй механику D&D 5e (кубики d20).
"""

# 1. Запуск игры
@router.message(Command("start_dnd"))
async def start_dnd_game(message: types.Message):
    user_id = message.from_user.id
    
    # Сбрасываем старую сессию, если была
    await execute_query("DELETE FROM dnd_sessions WHERE user_id = ?", (user_id,))
    
    # Создаем новую запись в БД
    await execute_query(
        "INSERT INTO dnd_sessions (user_id, session_state, players_data, current_location, last_response) VALUES (?, ?, ?, ?, ?)",
        (user_id, json.dumps({"history": []}), json.dumps({}), "Начало", "")
    )
    
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        welcome_prompt = "Приветствуй игроков, кратко опиши завязку сюжета и помоги нам создать персонажей."
        response = await ask_gemini(welcome_prompt, system_instruction=DM_PROMPT_TEMPLATE)
        
        # Сохраняем первый ответ
        await execute_query("UPDATE dnd_sessions SET last_response = ? WHERE user_id = ?", (response, user_id))
        
        await message.answer(response, reply_markup=get_dnd_actions_kb(), parse_mode="HTML")

@router.message(Command("stop_dnd"))
@router.message(F.text == "❌ Завершить игру")
async def stop_dnd_game(message: types.Message):
    user_id = message.from_user.id
    
    # 1. Проверяем, есть ли активная игра
    session = await fetch_one("SELECT * FROM dnd_sessions WHERE user_id = ?", (user_id,))
    
    if session:
        # 2. Удаляем сессию
        await execute_query("DELETE FROM dnd_sessions WHERE user_id = ?", (user_id,))
        
        # 3. Пишем сообщение об окончании и возвращаем кнопки из main_menu.py
        await message.answer(
            "🛑 <b>Игра окончена!</b>\n\nСессия удалена. Персонажи разошлись по домам, а DM закрыл свою книгу. Возвращаю основное меню.",
            reply_markup=get_main_kb(), # Та самая функция из main_menu.py
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Активных игр не найдено. Вот ваши основные кнопки:",
            reply_markup=get_main_kb()
        )

# 2. Основной обработчик всех текстовых действий
@router.message(F.text)
async def handle_dnd_action(message: types.Message):
    user_id = message.from_user.id
    user_action = message.text

    # Проверяем наличие сессии
    session = await fetch_one("SELECT * FROM dnd_sessions WHERE user_id = ?", (user_id,))
    if not session:
        return # Игнорируем, если игра не начата

    # Формируем промпт в зависимости от нажатой кнопки
    if user_action.startswith("Вариант "):
        choice = user_action.split(" ")[-1]
        prompt = f"Я выбираю вариант {choice}. Опиши последствия и продолжай приключение."
    elif user_action == "📊 Статус":
        prompt = "Покажи текущий статус персонажей и инвентарь в виде таблицы."
    elif user_action == "✍️ Свой вариант / Действие":
        await message.answer("Напиши текстом, что именно ты хочешь сделать.")
        return
    else:
        prompt = user_action

    # Запускаем "двигатель" игры
    await process_dnd_step(message, prompt)

# 3. Вспомогательная функция "двигатель" (process_dnd_step)
async def process_dnd_step(message: types.Message, user_input: str):
    user_id = message.from_user.id
    
    session = await fetch_one("SELECT session_state FROM dnd_sessions WHERE user_id = ?", (user_id,))
    history_data = json.loads(session['session_state'])
    history = history_data.get('history', [])

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        # Добавляем действие пользователя в контекст
        history.append({"role": "user", "parts": [user_input]})
        
        # Запрос к Gemini (передаем последние 10 сообщений для памяти)
        response_text = await ask_gemini(user_input, system_instruction=DM_PROMPT_TEMPLATE)

        # Генерируем изображение
        img_prompt = extract_image_description(response_text)
        image_url = await generate_image(img_prompt)

        # Сохраняем ответ модели в историю
        history.append({"role": "model", "parts": [response_text]})
        new_history_json = json.dumps({"history": history[-10:]})
        
        await execute_query(
            "UPDATE dnd_sessions SET session_state = ?, last_response = ? WHERE user_id = ?", 
            (new_history_json, response_text, user_id)
        )

        # Отправляем результат
        if len(response_text) > 1000:
            await message.answer_photo(photo=image_url)
            await message.answer(response_text, reply_markup=get_dnd_actions_kb(), parse_mode="HTML")
        else:
            await message.answer_photo(
                photo=image_url,
                caption=response_text,
                reply_markup=get_dnd_actions_kb(),
                parse_mode="HTML"
            )

# 4. Функция извлечения описания картинки
def extract_image_description(text: str) -> str:
    match = re.search(r"Описание для Изображения:\s*(.*?)(?=\n|$)", text)
    if match:
        return match.group(1).strip()
    return "fantasy adventure, epic scene, detailed illustration"