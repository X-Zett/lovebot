from io import BytesIO
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-3-flash-preview') # Основная модель для текста
image_model = genai.GenerativeModel('gemini-2.5-flash-image') # Модель для изображений (названия могут меняться)


# Настройка безопасности: отключаем блокировку по всем категориям
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# async def ask_gemini(prompt: str, system_instruction: str = "") -> str:
#     # ... (старый код ask_gemini остается без изменений) ...
#     try:
#         full_query = f"{system_instruction}\n\nЗапрос пользователя: {prompt}" if system_instruction else prompt
        
#         response = await model.generate_content_async(
#             full_query,
#             safety_settings=safety_settings,
#             request_options={"timeout": 60} # Увеличиваем тайм-аут для сложных ответов
#         )
        
#         if not response.candidates or not response.candidates[0].content.parts:
#             return "🤖 ИИ задумался слишком глубоко. Попробуй еще раз!"
            
#         return response.text
#     except Exception as e:
#         if "504" in str(e):
#             return "⏳ Сервера Google долго отвечают. Попробуй нажать кнопку еще раз через пару секунд."
#         return f"⚠️ Ошибка ИИ: {str(e)}"

async def ask_gemini(prompt: str, history: list = None, system_instruction: str = "") -> str:
    try:        
        # Создаем сессию чата с переданной историей
        # Если истории нет, передаем пустой список
        model = genai.GenerativeModel(
            model_name='gemini-3-flash-preview',
            system_instruction=system_instruction
        )
        chat = model.start_chat(history=history or [])
        
        # Отправляем сообщение
        response = await chat.send_message_async(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {str(e)}"

async def generate_image(description: str):
    try:
        # Модель Nano Banana создает изображение прямо в ответе
        response = await image_model.generate_content_async(description)
        
        # Извлекаем байты из первого парта первого кандидата
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                return BytesIO(part.inline_data.data)
        return None
    except Exception as e:
        logging.error(f"Nano Banana Error: {e}")
        return None