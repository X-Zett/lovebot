import json
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from utils.gemini_client import ask_gemini, generate_image
from database.db import execute_query, fetch_one
from keyboards.dnd_kb import get_dnd_actions_kb
from aiogram.utils.chat_action import ChatActionSender

router = Router()

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
Визуализация (Обязательно):
Локации: При каждом переходе в новую значимую локацию или начале важного события 
ты ОБЯЗАН описывать детали для генерации изображения.
Стиль: Иллюстрации должны быть детализированными, атмосферными и полностью 
соответствовать твоему описанию.
Интерфейс и Структура ответа (СТРОГО СОБЛЮДАЙ):
Заголовок локации: [Например: Глава 1: Туманные берега Шляпного залива]
Описание для Изображения: [КОРОТКОЕ И ТОЧНОЕ ОПИСАНИЕ СЦЕНЫ ДЛЯ ГЕНЕРАЦИИ КАРТИНКИ]
Повествование: Описание происходящего, диалоги, описание запахов, звуков и действий.
Статус Игроков (Таблица): 
| Игрок | Класс/Раса | HP | Инвентарь | Состояние | 
| :--- | :--- | :--- | :--- | :--- | 
| [Имя] | [Класс] | [HP]/[Max HP] | [Предмет 1, Предмет 2] | [Состояние] |
Действия: 
A. [Вариант действия 1]
B. [Вариант действия 2]
C. [Вариант действия 3]
D. [Вариант действия 4]
E. [Игрок может предложить свой вариант]
Правила игры:
Используй упрощенную механику D&D 5e. Если игроки совершают сложное действие, «бросай кубик» (d20) и описывай результат в зависимости от сложности (DC). Мир должен реагировать на решения.
---
{history_placeholder}
---
Начало:
Не начинай игру сразу. Сначала поприветствуй нас, кратко опиши завязку сюжета (заинтригуй!) и помоги нам создать персонажей (или предложи выбрать готовых). Как только мы подтвердим состав, сгенерируй первую локацию и начни приключение.
"""

# Хранилище для текущих активных действий (Reply-кнопок) по каждому пользователю
# В реальном проекте это тоже лучше хранить в БД, но для начала сойдет и в памяти
current_dnd_actions = {} 

@router.message(Command("start_dnd"))
async def start_dnd_game(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли активная сессия
    session = await fetch_one("SELECT * FROM dnd_sessions WHERE user_id = ?", (user_id,))
    if session:
        await message.answer("У вас уже есть активная D&D сессия! Продолжаем...", reply_markup=get_dnd_actions_kb(["Продолжить"]))
        return

    # Начинаем новую сессию, записываем стартовый промпт
    await execute_query(
        "INSERT INTO dnd_sessions (user_id, session_state, players_data, current_location, last_response) VALUES (?, ?, ?, ?, ?)",
        (user_id, json.dumps({"history": []}), json.dumps({}), "Начало", "")
    )
    
    # Первый запрос к DM
    dm_response = await ask_gemini(
        "Приветствуй игроков, кратко опиши завязку сюжета и предложи создать персонажей или выбрать готовых.",
        system_instruction=DM_PROMPT_TEMPLATE.format(history_placeholder="")
    )

    # Обновляем состояние сессии
    await execute_query(
        "UPDATE dnd_sessions SET last_response = ? WHERE user_id = ?",
        (dm_response, user_id)
    )
    
    # Извлекаем действия из ответа ИИ
    actions_text = dm_response.split("Действия:")[1] if "Действия:" in dm_response else ""
    actions_list = [line.strip()[2:] for line in actions_text.split('\n') if line.strip() and line.strip().startswith(('A.', 'B.', 'C.', 'D.', 'E.'))]
    
    current_dnd_actions[user_id] = actions_list # Сохраняем активные кнопки
    
    await message.answer(dm_response, reply_markup=get_dnd_actions_kb(actions_list))


@router.message(F.text) # Слушаем все текстовые сообщения, чтобы обрабатывать действия игроков
async def handle_dnd_action(message: types.Message):
    user_id = message.from_user.id
    user_action = message.text

    session = await fetch_one("SELECT * FROM dnd_sessions WHERE user_id = ?", (user_id,))
    if not session:
        # Если нет активной сессии, но пришло текстовое сообщение, игнорируем его
        # Или предлагаем начать игру
        return

    # Проверяем, является ли действие игрока одной из предложенных кнопок
    # или это пользовательский ответ
    possible_actions = current_dnd_actions.get(user_id, [])
    
    if user_action not in possible_actions and user_action != "Продолжить":
        # Это пользовательский вариант или нерелевантное сообщение
        if user_action.startswith(tuple("ABCDE.")):
            await message.answer("Пожалуйста, нажмите кнопку или введите свой вариант действия.", 
                                 reply_markup=get_dnd_actions_kb(possible_actions))
            return
        # Если это просто текст, который не является действием, то бот обрабатывает его как свой вариант
        # Или можно добавить логику, чтобы игнорировать неигровые сообщения
        # Для D&D мы предполагаем, что любой текст - это попытка игрока сделать что-то
        pass 
    
    # 1. Загружаем текущее состояние
    session_state = json.loads(session['session_state'])
    players_data = json.loads(session['players_data'])
    last_response = session['last_response']
    current_location = session['current_location']

    # Добавляем предыдущий ответ DM и текущее действие игрока в историю
    session_state['history'].append({"role": "model", "parts": [last_response]})
    session_state['history'].append({"role": "user", "parts": [f"Игрок совершает действие: {user_action}"]})

    # Сокращаем историю, чтобы не превышать лимиты токенов
    if len(session_state['history']) > 10: # Храним последние 10 обменов
        session_state['history'] = session_state['history'][-10:]

    # Собираем промпт для DM
    dm_prompt = f"Игрок выбрал действие: {user_action}. Продолжи историю. " \
                f"Учитывай текущее состояние игроков: {json.dumps(players_data)}. " \
                f"Не забудь соблюдать формат ответа: Заголовок, Описание для Изображения, Повествование, Статус Игроков, Действия."

    # Отправляем в Gemini
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        dm_full_response = await ask_gemini(
            dm_prompt,
            system_instruction=DM_PROMPT_TEMPLATE.format(history_placeholder=json.dumps(session_state['history']))
        )
    
    # 2. Парсим ответ DM
    # Ищем заголовок локации
    location_title_match = re.search(r"Заголовок локации:\s*(.*)", dm_full_response)
    location_title = location_title_match.group(1).strip() if location_title_match else "Неизвестная Локация"

    # Ищем описание для изображения
    image_desc_match = re.search(r"Описание для Изображения:\s*(.*)", dm_full_response)
    image_description = image_desc_match.group(1).strip() if image_desc_match else "фэнтези-сцена"

    # Извлекаем повествование, статус и действия
    # Это грубый парсинг, который нужно будет доработать
    parts = re.split(r"(Заголовок локации:|Описание для Изображения:|Повествование:|Статус Игроков \(Таблица\):|Действия:)", dm_full_response)
    
    narration = ""
    player_status_table = ""
    actions_text = ""
    
    # Пример парсинга (нужно улучшить регулярки)
    for i in range(len(parts)):
        if parts[i].strip() == "Повествование:":
            narration = parts[i+1].strip()
        elif parts[i].strip() == "Статус Игроков (Таблица):":
            player_status_table = parts[i+1].strip()
        elif parts[i].strip() == "Действия:":
            actions_text = parts[i+1].strip()

    # Собираем текст для отправки
    full_text_for_telegram = f"<b>{location_title}</b>\n\n{narration}\n\n{player_status_table}\n\n<b>Действия:</b>\n{actions_text}"
    
    # 3. Генерируем изображение
    image_url = await generate_image(image_description)
    
    # 4. Обновляем сессию в БД
    actions_list = [line.strip()[2:] for line in actions_text.split('\n') if line.strip() and line.strip().startswith(('A.', 'B.', 'C.', 'D.', 'E.'))]
    current_dnd_actions[user_id] = actions_list
    
    await execute_query(
        "UPDATE dnd_sessions SET session_state = ?, players_data = ?, current_location = ?, last_response = ? WHERE user_id = ?",
        (json.dumps(session_state), json.dumps(players_data), location_title, dm_full_response, user_id)
    )

    # 5. Отправляем сообщение с фото и кнопками
    await message.answer_photo(
        photo=image_url,
        caption=full_text_for_telegram,
        reply_markup=get_dnd_actions_kb(actions_list),
        parse_mode="HTML"
    )

# ... (другие хендлеры, например /stop_dnd, /show_status) ...