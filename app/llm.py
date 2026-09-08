import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL", "anthropic/claude-haiku-4-5")

if not API_KEY:
    raise RuntimeError("LLM_API_KEY is not set")


client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.proxyapi.ru/v1",
)


SYSTEM_PROMPT = """
Ты — классификатор обращений клиентов.

Твоя задача — проанализировать обращение и вернуть результат строго в JSON.

Допустимые категории:
- billing
- support
- complaint
- other

Допустимая confidence:
- high
- medium
- low

Поле escalate должно быть boolean.

draft_reply должен содержать короткий вежливый ответ клиенту
от 1 до 6 предложений.

Верни только JSON без markdown и без дополнительных пояснений.

Формат:
{
  "category": "billing",
  "draft_reply": "Короткий ответ клиенту.",
  "confidence": "high",
  "escalate": false
}
"""


def triage_with_llm(text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("LLM returned an empty response")

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    return json.loads(content)