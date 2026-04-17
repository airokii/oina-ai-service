from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import questions, emoji, crossword, theme

app = FastAPI(
    title="oina.click AI Service",
    description="AI микросервис для генерации контента игр и открыток",
    version="1.0.0"
)

# Разрешаем запросы с любого домена (нужно для связи с бэком)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(questions.router, prefix="/ai", tags=["Choose Me"])
app.include_router(emoji.router,     prefix="/ai", tags=["Guess by Emoji"])
app.include_router(crossword.router, prefix="/ai", tags=["Crossword"])
app.include_router(theme.router,     prefix="/ai", tags=["Theme"])

@app.get("/")
def root():
    return {"status": "ok", "service": "oina-ai-service"}

@app.get("/health")
def health():
    return {"status": "healthy"}
