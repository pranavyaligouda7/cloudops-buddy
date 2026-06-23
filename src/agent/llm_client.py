# src/agent/llm_client.py
from google import genai
from src.config.settings import settings

class GeminiClient:
    def __init__(self, model_name: str = None):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = model_name or settings.gemini_model

    def send_message(self, message: str, system_prompt: str = "") -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUser: {message}" if system_prompt else message
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")