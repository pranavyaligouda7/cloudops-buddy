# src/agent/llm_client_openai.py
from openai import OpenAI, RateLimitError
from src.config.settings import settings

class OpenAIClient:
    def __init__(self, model_name: str = None, base_url: str = None, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_base_url
        self.model_name = model_name or settings.openai_model

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

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
        except RateLimitError as e:
            # Handle quota exhaustion specifically
            raise RuntimeError(
                "OpenAI quota exhausted. Please add billing credits or switch to another provider."
            ) from e
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")