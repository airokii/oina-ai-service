from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from groq_client import call_groq

router = APIRouter()


# ── Модели данных ─────────────────────────────────────────────────────────────

class OutcomeItem(BaseModel):
    id: str    # "outcome_0"
    title: str # "Романтический ужин"


class PersonalityQuestionsRequest(BaseModel):
    topic: str = Field(..., description="Тема квиза", example="Свидание с Асель")
    outcomes: list[OutcomeItem] = Field(..., min_length=2, description="Возможные исходы квиза")
    count: Optional[int] = Field(5, ge=1, le=20, description="Количество вопросов")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class PersonalityOption(BaseModel):
    text: str
    outcomeId: str  # id из переданных outcomes


class PersonalityQuestion(BaseModel):
    question: str
    options: list[PersonalityOption]


class PersonalityQuestionsResponse(BaseModel):
    questions: list[PersonalityQuestion]


class GenerateOutcomesRequest(BaseModel):
    topic: str = Field(..., description="Тема квиза", example="Романтическое свидание")
    description: Optional[str] = Field("", description="Дополнительное описание")
    count: Optional[int] = Field(4, ge=2, le=10, description="Количество исходов")
    language: Optional[Literal["ru", "en", "kz"]] = "ru"


class OutcomeSuggestion(BaseModel):
    title: str


class GenerateOutcomesResponse(BaseModel):
    outcomes: list[OutcomeSuggestion]


# ── Эндпоинт ──────────────────────────────────────────────────────────────────

@router.post(
    "/generate-questions",
    response_model=PersonalityQuestionsResponse,
    summary="Генерация вопросов для квиза-личности Choose Me"
)
def generate_questions(body: PersonalityQuestionsRequest):
    """
    Creator вводит тему и список исходов → ИИ генерирует вопросы квиза-личности.

    Пример запроса:
    {
        "topic": "Свидание с Асель",
        "outcomes": [
            {"id": "outcome_0", "title": "Романтический ужин"},
            {"id": "outcome_1", "title": "Боулинг"},
            {"id": "outcome_2", "title": "Кино"}
        ],
        "count": 5,
        "language": "ru"
    }
    """

    outcomes_text = "\n".join([f"- {o.id}: {o.title}" for o in body.outcomes])
    valid_outcome_ids = {o.id for o in body.outcomes}

    prompt = f"""Ты генератор вопросов для квиза на платформе oina.click.

В этом квизе каждый ответ тайно ведёт к одному из заранее заданных исходов. Игрок не знает к какому — в конце подсчитывается, какой исход набрал больше всего выборов.

Тема: "{body.topic}"
Количество вопросов: {body.count}
Язык: {body.language}

Возможные исходы:
{outcomes_text}

ПРАВИЛА:
1. Каждый вариант ответа должен иметь outcomeId — один из id выше
2. Варианты ответа НЕ называют исход напрямую — они выражают предпочтения, поведение или ситуации, подходящие теме
3. Вопросы должны быть конкретными и соответствовать теме: "{body.topic}"
4. Ровно 2 варианта ответа на каждый вопрос
5. Распредели исходы между вопросами так, чтобы каждый исход встречался примерно одинаковое количество раз — не допускай чтобы один исход доминировал
6. Контент должен быть подходящим для всех возрастов

Верни ТОЛЬКО валидный JSON без пояснений:
{{
  "questions": [
    {{
      "question": "Текст вопроса?",
      "options": [
        {{"text": "Вариант А", "outcomeId": "outcome_0"}},
        {{"text": "Вариант Б", "outcomeId": "outcome_1"}}
      ]
    }}
  ]
}}"""

    try:
        result = call_groq(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    # Валидация: ровно 2 варианта и все outcomeId из переданного списка
    questions = result.get("questions", [])
    for q in questions:
        options = q.get("options", [])
        if len(options) != 2:
            raise HTTPException(
                status_code=502,
                detail=f"AI returned {len(options)} options instead of 2"
            )
        for opt in options:
            if opt.get("outcomeId") not in valid_outcome_ids:
                raise HTTPException(
                    status_code=502,
                    detail=f"AI returned unknown outcomeId: {opt.get('outcomeId')}"
                )

    return result


@router.post(
    "/generate-outcomes",
    response_model=GenerateOutcomesResponse,
    summary="Генерация вариантов исходов для квиза Choose Me"
)
def generate_outcomes(body: GenerateOutcomesRequest):
    """
    Creator вводит тему → ИИ предлагает варианты исходов.

    Пример запроса:
    {
        "topic": "Свидание",
        "description": "Место для первого свидания с Асель",
        "count": 4,
        "language": "ru"
    }
    """

    description_line = f'Описание: "{body.description}"' if body.description and body.description.strip() else ""

    prompt = f"""Ты помогаешь создать квиз на платформе oina.click.

В этом квизе игрок отвечает на вопросы и в конце получает один из возможных исходов.

Тема: "{body.topic}"
{description_line}
Количество исходов: {body.count}
Язык: {body.language}

Придумай {body.count} разных, конкретных и интересных исходов для этой темы.
Исходы должны быть разными по характеру — не похожими друг на друга.

Верни ТОЛЬКО валидный JSON без пояснений:
{{
  "outcomes": [
    {{"title": "Название исхода"}},
    {{"title": "Другой исход"}}
  ]
}}"""

    try:
        result = call_groq(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    outcomes = result.get("outcomes", [])
    if len(outcomes) < 2:
        raise HTTPException(status_code=502, detail="AI returned too few outcomes")

    return result
