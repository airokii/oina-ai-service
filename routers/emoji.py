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
    emojis: list[str]       # например ["🦁", "👑"]
    answer: str             # например "Король Лев"
    hint: Optional[str]     # короткая подсказка или null


class EmojiResponse(BaseModel):
    puzzles: list[EmojiPuzzle]


class EmojiHintRequest(BaseModel):
    mode: Literal[
        "emojis-from-answer",   # есть слово → AI предлагает эмодзи
        "answer-from-emojis",   # есть эмодзи → AI предлагает ответ
        "hint-from-answer",     # есть ответ → AI пишет подсказку
    ]
    input: str = Field(..., description="Слово, эмодзи-строка или ответ")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class EmojiHintResponse(BaseModel):
    result: str
    alternatives: list[str]


# ── Эндпоинты ──────────────────────────────────────────────────────────────────

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
      "emojis": ["🦁", "👑"],
      "answer": "Король Лев",
      "hint": "Мультфильм Disney"
    }}
  ]
}}

Правила:
- emojis — массив из 2-4 отдельных эмодзи (каждый элемент — один эмодзи)
- Ответы должны быть узнаваемыми словами или фразами
- hint — короткая подсказка (можно null)
- Делай загадки разной сложности
- Не придумывай факты"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.post(
    "/generate-emoji-hint",
    response_model=EmojiHintResponse,
    summary="Per-puzzle AI подсказка для редактора Guess by Emoji"
)
def generate_emoji_hint(body: EmojiHintRequest):
    """
    Три режима работы:
    - emojis-from-answer: creator ввёл слово → AI предлагает эмодзи
    - answer-from-emojis: creator ввёл эмодзи → AI предлагает ответ
    - hint-from-answer: creator ввёл ответ → AI пишет подсказку
    """

    if body.mode == "emojis-from-answer":
        prompt = f"""Ты помогаешь создавать эмодзи-загадки.

Слово/фраза: "{body.input}"
Язык: {body.language}

Предложи 2-4 эмодзи, которые лучше всего передают это слово/фразу.
Дай 2 альтернативных варианта эмодзи-комбо для того же слова.

Верни ТОЛЬКО JSON без пояснений:
{{
  "result": "🦁👑",
  "alternatives": ["🎭👑", "🌅🦁"]
}}"""

    elif body.mode == "answer-from-emojis":
        prompt = f"""Ты помогаешь создавать эмодзи-загадки.

Эмодзи-последовательность: "{body.input}"
Язык: {body.language}

Предложи наиболее подходящее слово или фразу-ответ для этих эмодзи.
Дай 2 альтернативных варианта ответа.

Верни ТОЛЬКО JSON без пояснений:
{{
  "result": "Король Лев",
  "alternatives": ["Лев-победитель", "Царь зверей"]
}}"""

    else:  # hint-from-answer
        prompt = f"""Ты помогаешь создавать эмодзи-загадки.

Слово/фраза-ответ: "{body.input}"
Язык: {body.language}

Напиши короткую подсказку (3-7 слов) для этого слова, не называя его напрямую.
Дай 2 альтернативных варианта подсказки.

Верни ТОЛЬКО JSON без пояснений:
{{
  "result": "Мультфильм Disney про саванну",
  "alternatives": ["Знаменитый мультфильм с Симбой", "История льва и его королевства"]
}}"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
