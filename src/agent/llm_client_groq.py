# src/agent/llm_client_groq.py
from groq import Groq
from src.config.settings import settings

class GroqClient:
    def __init__(self, model_name: str = None):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = model_name or settings.groq_model

    def send_message(self, message: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")