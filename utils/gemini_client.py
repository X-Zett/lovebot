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
    """
    Универсальная функция: принимает промпт и (опционально) роль/настройку.
    """
    try:
        # Объединяем инструкцию и запрос
        full_query = f"{system_instruction}\n\nЗапрос пользователя: {prompt}" if system_instruction else prompt
        
        response = await model.generate_content_async(full_query)
        return response.text
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {str(e)}"