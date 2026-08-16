"""Lapisan abstraksi untuk model bahasa.

Bagian lain aplikasi cukup memanggil generate() tanpa perlu tahu
penyedia mana yang dipakai di baliknya.
"""

from app.core.config import settings


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, user_message: str, system_prompt: str, temperature: float) -> str:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
        return response.text


class GroqClient:
    def __init__(self, api_key: str, model: str) -> None:
        from groq import Groq

        self._client = Groq(api_key=api_key)
        self._model = model

    def generate(self, user_message: str, system_prompt: str, temperature: float) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content


def build_client(provider: str):
    """Membuat client sesuai penyedia yang diminta."""
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY kosong. Cek file .env kamu.")
        return GroqClient(settings.GROQ_API_KEY, settings.GROQ_MODEL)

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY kosong. Cek file .env kamu.")
        return GeminiClient(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)

    raise ValueError(f"Penyedia tidak dikenal: {provider}")


class LLMClient:
    """Pembungkus yang memilih penyedia berdasarkan konfigurasi."""

    def __init__(self, provider: str | None = None) -> None:
        self._provider = provider or settings.LLM_PROVIDER
        self._impl = build_client(self._provider)

    @property
    def provider(self) -> str:
        return self._provider

    def generate(self, user_message: str, system_prompt: str | None = None) -> str:
        return self._impl.generate(
            user_message=user_message,
            system_prompt=system_prompt or settings.SYSTEM_PROMPT,
            temperature=settings.TEMPERATURE,
        )


llm_client = LLMClient()