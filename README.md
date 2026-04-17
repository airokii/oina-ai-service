# oina-ai-service

AI микросервис для платформы oina.click.
Генерирует контент для игр Choose Me, Guess by Emoji, Crossword и подбирает темы.

## Стек
- Python 3.10+
- FastAPI
- Groq API (Llama 3.1 — бесплатно)

## Структура
```
oina-ai-service/
├── main.py              — точка входа, FastAPI приложение
├── groq_client.py       — клиент для Groq API
├── requirements.txt     — зависимости
├── Procfile             — для деплоя на Railway
├── .env.example         — шаблон переменных окружения
└── routers/
    ├── questions.py     — POST /ai/generate-questions
    ├── emoji.py         — POST /ai/generate-emoji
    ├── crossword.py     — POST /ai/generate-crossword
    └── theme.py         — POST /ai/suggest-theme
```

## Запуск локально

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Создать .env файл
```bash
copy .env.example .env
```
Открыть .env и вставить свой Groq API ключ.

### 3. Запустить сервер
```bash
uvicorn main:app --reload
```

Сервис запустится на http://localhost:8000

Документация (Swagger UI): http://localhost:8000/docs

## API эндпоинты

| Метод | Путь                      | Игра            |
|-------|---------------------------|-----------------|
| POST  | /ai/generate-questions    | Choose Me       |
| POST  | /ai/generate-emoji        | Guess by Emoji  |
| POST  | /ai/generate-crossword    | Crossword       |
| POST  | /ai/suggest-theme         | Тема/фон        |

## Примеры запросов

### Choose Me
```json
POST /ai/generate-questions
{
  "topic": "Казахстан",
  "count": 5,
  "language": "ru"
}
```

### Guess by Emoji
```json
POST /ai/generate-emoji
{
  "topic": "казахская культура",
  "count": 5,
  "language": "ru"
}
```

### Crossword (слово → определение)
```json
POST /ai/generate-crossword
{
  "mode": "definition-from-word",
  "input": "ДОМБЫРА",
  "language": "ru"
}
```

### Crossword (определение → слово)
```json
POST /ai/generate-crossword
{
  "mode": "word-from-definition",
  "input": "Казахский народный инструмент",
  "language": "ru"
}
```

### Тема/фон
```json
POST /ai/suggest-theme
{
  "description": "весёлая викторина про Казахстан",
  "language": "ru"
}
```

## Деплой на Railway

1. Создай репозиторий на GitHub и залей туда эту папку
2. Зайди на railway.app → New Project → Deploy from GitHub
3. Выбери репозиторий
4. В Settings → Variables добавь: GROQ_API_KEY=gsk_...
5. Railway автоматически запустит сервис
6. Скопируй публичный URL и передай бэкендеру
