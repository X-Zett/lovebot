import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview') # Основная модель для текста
image_model = genai.GenerativeModel('gemini-2.5-flash-image') # Модель для изображений (названия могут меняться)


# Настройка безопасности: отключаем блокировку по всем категориям
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

async def ask_gemini(prompt: str, system_instruction: str = "") -> str:
    # ... (старый код ask_gemini остается без изменений) ...
    try:
        full_query = f"{system_instruction}\n\nЗапрос пользователя: {prompt}" if system_instruction else prompt
        
        response = await model.generate_content_async(
            full_query,
            safety_settings=safety_settings,
            request_options={"timeout": 60} # Увеличиваем тайм-аут для сложных ответов
        )
        
        if not response.candidates or not response.candidates[0].content.parts:
            return "🤖 ИИ задумался слишком глубоко. Попробуй еще раз!"
            
        return response.text
    except Exception as e:
        if "504" in str(e):
            return "⏳ Сервера Google долго отвечают. Попробуй нажать кнопку еще раз через пару секунд."
        return f"⚠️ Ошибка ИИ: {str(e)}"

async def generate_image(description: str) -> str:
    """
    Генерирует изображение на основе текстового описания.
    Возвращает URL изображения.
    """
    try:
        # Промпт для генерации изображения
        image_prompt = (
            f"Создай детализированную, атмосферную фэнтези-иллюстрацию в стиле D&D "
            f"для следующей сцены: {description}. Учти, что это часть эпического, но "
            f"иногда абсурдного приключения. Изображение должно точно соответствовать описанию."
        )
        
        response = await image_model.generate_content_async(
            image_prompt,
            safety_settings=safety_settings,
            request_options={"timeout": 75}
        )
        
        # Предполагаем, что response.candidates[0].content.parts[0].image.uri содержит URL
        # В реальной интеграции с Gemini Image API, ты получишь объект Image.
        # Для Telegram тебе нужен будет URL или Base64.
        # Если API выдает сразу URL:
        if response.candidates and response.candidates[0].content.parts:
            # Здесь может быть сложнее, API Gemini Image обычно возвращает объект Image
            # который нужно либо сохранить локально, либо получить его прямую ссылку.
            # Для тестовых целей пока вернем заглушку или условный URL.
            # В реальной интеграции Image API может вернуть объект или Base64.
            # Если это Base64, нужно будет его декодировать и загрузить в Telegram.
            # Для упрощения, пока представим, что мы получаем URL:
            return "https://picsum.photos/1280/720" # <--- Заглушка, пока не будет реального API
        
        return "https://picsum.photos/1280/720" # Заглушка, если что-то пошло не так
    except Exception as e:
        logging.error(f"Ошибка при генерации изображения: {e}")
        return "https://picsum.photos/1280/720" # Заглушка при ошибке