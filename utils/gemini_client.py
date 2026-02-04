import google.generativeai as genai
import os
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview') # 3 Flash (2026)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

async def ask_gemini(prompt: str, system_instruction: str = "") -> str:
    try:
        full_query = f"{system_instruction}\n\nЗапрос пользователя: {prompt}" if system_instruction else prompt
        
        # Добавляем safety_settings в запрос
        response = await model.generate_content_async(
            full_query,
            safety_settings=safety_settings
        )
        
        # Проверка: если ответ всё равно пустой (бывает при технических сбоях)
        if not response.candidates or not response.candidates[0].content.parts:
            return "🤖 ИИ промолчал... Возможно, ситуация слишком абсурдна даже для него. Попробуй еще раз!"
            
        return response.text
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {str(e)}"