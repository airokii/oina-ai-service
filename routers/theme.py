from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from groq_client import call_groq

router = APIRouter()


# ── Модели данных ─────────────────────────────────────────────────────────────

class ThemeRequest(BaseModel):
    description: str = Field(
        ...,
        description="Описание настроения или темы",
        example="нежный день рождения для подруги"
    )
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class ThemeSuggestion(BaseModel):
    name: str               # название темы
    backgroundColor: str    # hex, например "#FFF0F5"
    accentColor: str        # hex
    textColor: str          # hex
    emoji: str              # эмодзи настроения
    description: str        # короткое описание для creator'а


class ThemeResponse(BaseModel):
    themes: list[ThemeSuggestion]  # всегда 3 варианта


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/suggest-theme",
    response_model=ThemeResponse,
    summary="Подбор цветовой темы для игры или открытки"
)
def suggest_theme(body: ThemeRequest):
    """
    Creator описывает настроение словами → ИИ предлагает 3 цветовые темы с hex-кодами.

    Пример запроса:
    {
        "description": "весёлая викторина про Казахстан",
        "language": "ru"
    }
    """

    prompt = f"""Предложи 3 цветовые темы для игры или открытки по описанию: "{body.description}".
Язык названий и описаний: {body.language}.

Верни ТОЛЬКО JSON:
{{
  "themes": [
    {{
      "name": "Название темы",
      "backgroundColor": "#FFE4E1",
      "accentColor": "#FF6B9D",
      "textColor": "#2D2D2D",
      "emoji": "🌸",
      "description": "Короткое описание для пользователя"
    }}
  ]
}}

Правила:
- Ровно 3 темы которые визуально отличаются друг от друга
- Все цвета в формате HEX (#RRGGBB)
- backgroundColor — светлый/пастельный для читаемости
- textColor — тёмный для контраста с backgroundColor
- emoji отражает настроение темы"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
