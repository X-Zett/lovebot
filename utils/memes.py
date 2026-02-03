import aiohttp
import random
import logging

async def get_random_meme():
    # Список сабреддитов под ваши интересы
    subreddits = [
        "me_irl",               # Жизненно и тревожно
        "relationshipmemes",    # Про любовь
        "linguisticshumor",     # Про языки (английский/французский)
        "bookmemes",            # Про книги
        "gamingmemes",          # Про игры
        "okbuddyretard",        # Абсурдный и "глупый" юмор
    ]
    
    selected_sub = random.choice(subreddits)
    url = f"https://meme-api.com/gimme/{selected_sub}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "url": data.get('url'),
                        "title": data.get('title', 'Без названия'),
                        "sub": selected_sub # Добавим, чтобы знать откуда мем
                    }
                return None
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return None