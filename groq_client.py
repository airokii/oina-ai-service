import os
import json
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Ты — AI ассистент платформы oina.click для создания игр и открыток.
Всегда отвечай ТОЛЬКО валидным JSON без markdown, без пояснений, без лишнего текста.
Первый символ ответа должен быть { или ["""


def call_groq(prompt: str) -> dict:
    completion = client.chat.completions.create(
        model=MODEL,
        temperature=0.7,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    raw = completion.choices[0].message.content
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)