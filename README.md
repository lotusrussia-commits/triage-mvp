# Triage MVP

MVP-сервис для автоматической обработки обращений клиентов с помощью LLM.

## Возможности

* принимает обращения клиентов через `POST /triage`;
* классифицирует обращения по категориям:

  * `billing`
  * `support`
  * `complaint`
  * `other`
* формирует черновик ответа клиенту;
* определяет уровень уверенности `high / medium / low`;
* определяет, требуется ли передача оператору;
* сохраняет обращения и результаты обработки в SQLite;
* ограничивает количество запросов от одного `client_id`;
* при ошибке LLM автоматически возвращает ответ «Передано оператору.» и сохраняет информацию об ошибке;
* ведёт логи обработки запросов.

## Технологии

* Python 3.12
* FastAPI
* Pydantic
* SQLite
* ProxyAPI
* OpenAI-compatible API
* Uvicorn

## Структура проекта

```text
triage-mvp/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── llm.py
│   ├── main.py
│   └── models.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── test_llm.py
```

Файлы `.env` и `triage.db` создаются локально и не добавляются в Git.

## Установка

Клонировать репозиторий:

```bash
git clone https://github.com/lotusrussia-commits/triage-mvp.git
cd triage-mvp
```

Создать виртуальное окружение:

```bash
python3 -m venv .venv
```

Активировать его:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
python -m pip install -r requirements.txt
```

## Настройка переменных окружения

Создать файл `.env`:

```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=anthropic/claude-haiku-4-5
```

API-ключ хранится только в `.env` и не добавляется в Git.

## Запуск

Запустить приложение:

```bash
python -m uvicorn app.main:app --reload
```

После запуска:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Пример запроса

```json
{
  "text": "Подскажите, как изменить пароль?",
  "channel": "chat",
  "client_id": "client-001"
}
```

Пример ответа:

```json
{
  "category": "support",
  "draft_reply": "Спасибо за обращение! Для изменения пароля перейдите в настройки аккаунта и выберите раздел безопасности.",
  "confidence": "high",
  "escalate": false
}
```

## Ограничение запросов

Для одного `client_id` разрешено не более 5 запросов за 60 секунд.

При превышении лимита API возвращает:

```text
429 Too Many Requests
```

## Обработка ошибки LLM

Если LLM недоступна или возвращает ошибку, сервис не падает.

Возвращается:

```json
{
  "category": "other",
  "draft_reply": "Передано оператору.",
  "confidence": "low",
  "escalate": true
}
```

Информация об ошибке сохраняется в SQLite.

## Логи

Сервис записывает в лог:

* получение запроса;
* `client_id` и канал;
* результат классификации;
* уровень confidence;
* значение escalate;
* превышение rate limit;
* ошибки LLM;
* использование fallback-ответа.

## Проверенные сценарии

В ходе разработки проверены:

1. Успешная обработка обращения через LLM.
2. Валидация входных данных.
3. Ограничение запросов по `client_id`.
4. Сохранение результатов в SQLite.
5. Обработка ошибки LLM и fallback.
6. Логирование запросов и результатов.
