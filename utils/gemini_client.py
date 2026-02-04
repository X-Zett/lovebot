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

async def generate_image(description: str):
    """
    Генерирует изображение через Gemini 2.5 Flash Image (Nano Banana).
    """
    try:
        # Улучшаем промпт для D&D стиля
        refined_prompt = f"Fantasy D&D illustration, high quality digital art: {description}"
        
        # В этой модели генерация идет через generate_content
        # Но возвращается объект, содержащий данные изображения
        response = await image_model.generate_content_async(refined_prompt)
        
        # Проверяем, есть ли изображение в ответе
        # Обычно это один из вариантов (candidates)
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data: # Если данные пришли в бинарном виде
                    img_data = part.inline_data.data
                    return BytesIO(img_data)
                # Если API возвращает объект Image (зависит от версии SDK)
                elif hasattr(part, 'image'):
                    img_byte_arr = BytesIO()
                    part.image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    return img_byte_arr

        return None
    except Exception as e:
        print(f"Ошибка генерации Nano Banana: {e}")
        return None