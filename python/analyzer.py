import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Ты — ассистент для обработки протоколов совещаний на русском языке.
Проанализируй транскрипт и верни ТОЛЬКО валидный JSON без markdown.

{
  "meeting": {
    "title": "название совещания",
    "participants": [{"name": "Имя или Спикер N", "role": "Председатель | Докладчик | Участник | Секретарь"}]
  },
  "summary": "саммари 4-12 предложений",
  "sentiment": "тональность встречи — одно из: Конструктивная (деловое обсуждение, договорённости), Позитивная (радость, согласие), Нейтральная (информационный обмен без эмоций), Напряжённая (конфликт, претензии, давление). Выбирай точно по содержанию, не по умолчанию.",
  "keywords": ["слово1", "слово2"],
  "contacts": [{"name": "Имя", "email": null, "phone": null, "position": null}],
  "decisions": ["решение 1"],
  "tasks": [{"assignee": "Имя", "task": "описание", "deadline": null, "priority": "Высокий | Средний | Низкий"}],
  "next_meeting": null
}

Правила:
- Если информации нет — null или [].
- Роли определяй по поведению в диалоге.
- keywords — 5-10 ключевых тем.
- Задачи: глагол + объект + результат.
- sentiment: НЕ выбирай Напряжённую по умолчанию. Напряжённая — только если есть явный конфликт, претензии или агрессия. Обычное рабочее совещание = Конструктивная. Нет явных эмоций = Нейтральная."""


def analyze_transcript(text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Транскрипт:\n\n{text}"},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        for part in raw.split("```")[1:]:
            part = part.strip()
            if part.startswith("json"): part = part[4:].strip()
            if part.startswith("{"): raw = part; break
    return json.loads(raw[:raw.rfind("}")+1])