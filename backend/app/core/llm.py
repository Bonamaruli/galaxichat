from google import genai
from google.genai import types

from app.core.config import settings


class LLMClient:
    """Lapisan pembungkus untuk berbicara dengan model bahasa.

    Bagian lain aplikasi cukup memanggil generate() tanpa perlu tahu
    model apa yang dipakai di baliknya.
    """

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.GEMINI_MODEL

    def generate(self, user_message: str, system_prompt: str | None = None) -> str:
        instruction = system_prompt or settings.SYSTEM_PROMPT

        response = self._client.models.generate_content(
            model=self._model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=settings.TEMPERATURE,
            ),
        )
        return response.text


llm_client = LLMClient()