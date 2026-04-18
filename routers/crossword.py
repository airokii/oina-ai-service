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
    result: str
    alternatives: list[str]


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/generate-crossword",
    response_model=CrosswordResponse,
    summary="AI подсказка для кроссворда"
)
def generate_crossword(body: CrosswordRequest):
    if body.mode == "definition-from-word":
        prompt = f"""Ты помощник для кроссвордов. Тебе дано слово, нужно написать краткое определение.

Слово: "{body.input}"
Язык определения: {body.language}

Правила:
- Пиши ТОЛЬКО то что точно знаешь об этом слове
- Определение: 3-7 слов, без использования самого слова или однокоренных
- Дай 2 альтернативных определения того же слова
- Если не знаешь слово точно — пиши общее нейтральное описание

Верни ТОЛЬКО JSON без пояснений:
{{
  "result": "краткое определение слова",
  "alternatives": ["второй вариант определения", "третий вариант определения"]
}}"""

    else:
        prompt = f"""Ты помощник для кроссвордов. Тебе дано определение, нужно предложить подходящее слово.

Определение: "{body.input}"
Язык: {body.language}

Правила:
- Предложи наиболее подходящее слово для этого определения
- Слово должно быть одним словом без пробелов, заглавными буквами
- Предложи 2 альтернативных слова которые тоже могут подойти
- Выбирай только распространённые общеизвестные слова

Верни ТОЛЬКО JSON без пояснений:
{{
  "result": "СЛОВО",
  "alternatives": ["СЛОВО2", "СЛОВО3"]
}}"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
