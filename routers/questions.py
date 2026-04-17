from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from groq_client import call_groq

router = APIRouter()


# ── Модели данных (что принимаем и что возвращаем) ────────────────────────────

class QuestionsRequest(BaseModel):
    topic: str = Field(..., description="Тема викторины", example="Казахстан")
    count: Optional[int] = Field(5, ge=1, le=20, description="Количество вопросов")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class QuizQuestion(BaseModel):
    question: str
    options: list[str]      # всегда 4 варианта
    correctIndex: int       # 0, 1, 2 или 3


class QuestionsResponse(BaseModel):
    questions: list[QuizQuestion]


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/generate-questions",
    response_model=QuestionsResponse,
    summary="Генерация вопросов для викторины Choose Me"
)
def generate_questions(body: QuestionsRequest):
    """
    Creator вводит тему → ИИ генерирует вопросы с 4 вариантами ответа.

    Пример запроса:
    {
        "topic": "Казахстан",
        "count": 5,
        "language": "ru"
    }
    """

    # ── Промпт для Groq ───────────────────────────────────────────────────────
    #
    # Мы говорим модели:
    # 1. Что генерировать (вопросы для викторины)
    # 2. На какую тему
    # 3. Точный формат JSON который ожидаем
    # 4. Правила которые нужно соблюдать
    #
    prompt = f"""Сгенерируй {body.count} вопросов для викторины на тему: "{body.topic}".
Язык: {body.language}.

Верни ТОЛЬКО JSON в таком формате:
{{
  "questions": [
    {{
      "question": "Текст вопроса?",
      "options": ["Вариант А", "Вариант Б", "Вариант В", "Вариант Г"],
      "correctIndex": 0
    }}
  ]
}}

Правила:
- Ровно 4 варианта ответа в каждом вопросе
- correctIndex — индекс правильного ответа (0, 1, 2 или 3)
- Чередуй позицию правильного ответа — не всегда 0
- Вопросы должны быть интересными и понятными широкой аудитории"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
