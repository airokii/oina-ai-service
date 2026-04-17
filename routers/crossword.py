from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from groq_client import call_groq

router = APIRouter()


# ── Модели данных ─────────────────────────────────────────────────────────────

class CrosswordRequest(BaseModel):
    mode: Literal["word-from-definition", "definition-from-word"] = Field(
        ...,
        description=(
            "word-from-definition → creator ввёл определение, ИИ предлагает слово. "
            "definition-from-word → creator ввёл слово, ИИ придумывает определение."
        )
    )
    input: str = Field(..., description="Слово или определение от creator'а", example="ДОМБЫРА")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class CrosswordResponse(BaseModel):
    result: str             # главный ответ
    alternatives: list[str] # 2 альтернативных варианта


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/generate-crossword",
    response_model=CrosswordResponse,
    summary="AI подсказка для кроссворда"
)
def generate_crossword(body: CrosswordRequest):
    """
    Два режима работы:

    1. definition-from-word: creator ввёл слово "ДОМБЫРА"
       → ИИ придумывает определение: "Традиционный казахский струнный инструмент"

    2. word-from-definition: creator ввёл определение "Казахский народный инструмент"
       → ИИ предлагает слово: "ДОМБЫРА"

    Пример запроса:
    {
        "mode": "definition-from-word",
        "input": "ДОМБЫРА",
        "language": "ru"
    }
    """

    # Выбираем разный промпт в зависимости от режима
    if body.mode == "definition-from-word":
        prompt = f"""Придумай краткое определение для кроссворда к слову: "{body.input}".
Язык: {body.language}.

Верни ТОЛЬКО JSON:
{{
  "result": "Краткое определение (до 8 слов)",
  "alternatives": ["Второй вариант определения", "Третий вариант"]
}}

Правила:
- Определение должно быть кратким — до 8 слов
- Не используй однокоренные слова в определении
- alternatives — ровно 2 альтернативных варианта"""

    else:  # word-from-definition
        prompt = f"""Предложи слово для кроссворда по определению: "{body.input}".
Язык: {body.language}.

Верни ТОЛЬКО JSON:
{{
  "result": "СЛОВО",
  "alternatives": ["СЛОВО2", "СЛОВО3"]
}}

Правила:
- Слово заглавными буквами без пробелов
- alternatives — ровно 2 альтернативных варианта
- Выбирай распространённые слова"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
