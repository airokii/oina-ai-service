from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from groq_client import call_groq

router = APIRouter()


# ── Модели данных ─────────────────────────────────────────────────────────────

class EmojiRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Тема загадок", example="мультфильмы")
    count: Optional[int] = Field(5, ge=1, le=20, description="Количество загадок")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class EmojiPuzzle(BaseModel):
    emojis: str             # например "🦁👑"
    answer: str             # например "Король Лев"
    hint: Optional[str]     # короткая подсказка или null


class EmojiResponse(BaseModel):
    puzzles: list[EmojiPuzzle]


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/generate-emoji",
    response_model=EmojiResponse,
    summary="Генерация загадок для игры Guess by Emoji"
)
def generate_emoji(body: EmojiRequest):
    """
    Creator выбирает тему (опционально) → ИИ генерирует загадки: эмодзи → слово.

    Пример запроса:
    {
        "topic": "казахская культура",
        "count": 5,
        "language": "ru"
    }
    """

    topic_line = f'Тема: "{body.topic}".' if body.topic else "Тема: любая популярная и узнаваемая."

    prompt = f"""Сгенерируй {body.count} эмодзи-загадок — угадай слово или фразу по эмодзи.
{topic_line}
Язык ответов: {body.language}.

Верни ТОЛЬКО JSON:
{{
  "puzzles": [
    {{
      "emojis": "🦁👑",
      "answer": "Король Лев",
      "hint": "Мультфильм Disney"
    }}
  ]
}}

Правила:
- 2-4 эмодзи на загадку
- Ответы должны быть узнаваемыми словами или фразами
- hint — короткая подсказка (можно null)
- Делай загадки разной сложности"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
