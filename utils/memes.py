import aiohttp
import logging

async def get_random_meme():
    # Используем проверенное API для мемов
    url = "https://meme-api.com/gimme/memes"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Проверяем, что пришла картинка, а не видео/гифка (опционально)
                    return {
                        "url": data.get('url'),
                        "title": data.get('title', 'Без названия')
                    }
                else:
                    logging.error(f"API мемов ответило статусом: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к API мемов: {e}")
        return None