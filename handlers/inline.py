import hashlib
import random
from aiogram import Router, types
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from database.db import fetch_all

router = Router()

@router.inline_query()
async def inline_handler(query: InlineQuery):
    text = query.query.strip()
    results = []

    # РЕЖИМ 1: Колесо фортуны (если введен текст через запятую)
    if text and "," in text:
        options = [opt.strip() for opt in text.split(",") if opt.strip()]
        if len(options) > 1:
            choice = random.choice(options)
            result_id = hashlib.md5(f"choice_{text}".encode()).hexdigest()
            
            results.append(
                InlineQueryResultArticle(
                    id=result_id,
                    title="🎲 Определить судьбу",
                    description=f"Выбрать из: {', '.join(options)}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"🎲 В споре между <b>{text}</b> судьба выбрала: <b>{choice}</b>",
                        parse_mode="HTML"
                    )
                )
            )

    # РЕЖИМ 2: Список желаний (всегда показываем, если база не пуста)
    rows = await fetch_all("SELECT text FROM wishes LIMIT 10")
    for i, row in enumerate(rows):
        wish_text = row['text']
        # Генерируем уникальный ID для каждого результата
        result_id = hashlib.md5(f"wish_{i}_{wish_text}".encode()).hexdigest()
        
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title="🤫 Мое секретное желание",
                description=wish_text[:40] + "...", # Короткое превью
                input_message_content=InputTextMessageContent(
                    message_text=f"🤫 Одно из моих желаний: <i>{wish_text}</i>",
                    parse_mode="HTML"
                )
            )
        )

    # Отправляем результаты (cache_time=0 для тестов, чтобы результаты обновлялись сразу)
    await query.answer(results, cache_time=1)