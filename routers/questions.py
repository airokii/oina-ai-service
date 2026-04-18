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
    prompt = f"""Ты генератор вопросов для образовательной викторины на платформе oina.click.
 
Тема викторины: "{body.topic}"
Количество вопросов: {body.count}
Язык: {body.language}
 
СТРОГИЕ ПРАВИЛА:
1. Генерируй ТОЛЬКО вопросы по указанной теме
2. Пиши ТОЛЬКО проверенные факты — не выдумывай ничего
3. Если не уверен в факте — не включай такой вопрос
4. Контент должен быть подходящим для всех возрастов (семейный)
5. Никакого насилия, политики, религиозных споров, 18+ контента
6. Ровно 4 варианта ответа на каждый вопрос
7. correctIndex — индекс правильного ответа (0, 1, 2 или 3)
8. ОБЯЗАТЕЛЬНО чередуй correctIndex — используй разные значения 0, 1, 2, 3

 
Верни ТОЛЬКО валидный JSON без пояснений и markdown:
{{
  "questions": [
    {{
      "question": "Текст вопроса?",
      "options": ["Вариант А", "Вариант Б", "Вариант В", "Вариант Г"],
      "correctIndex": 1
    }}
  ]
}}"""

    try:
        result = call_groq(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
