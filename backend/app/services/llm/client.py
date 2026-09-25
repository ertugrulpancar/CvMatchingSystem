from functools import lru_cache

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import get_settings


class GeminiError(Exception):
    pass


@lru_cache
def _get_client() -> genai.Client:
    return genai.Client(api_key=get_settings().gemini_api_key)


def generate_structured[T: BaseModel](prompt: str, response_schema: type[T]) -> T:
    settings = get_settings()

    try:
        response = _get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
    except Exception as exc:
        raise GeminiError(f"Gemini isteği başarısız oldu: {exc}") from exc

    if not isinstance(response.parsed, response_schema):
        raise GeminiError("Gemini geçersiz bir yanıt döndürdü")

    return response.parsed
