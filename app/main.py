from collections import defaultdict
from time import time
import logging

from fastapi import FastAPI, HTTPException

from app.database import init_db, save_ticket
from app.llm import triage_with_llm
from app.models import TriageRequest, TriageResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(title="Triage MVP")


init_db()


RATE_LIMIT = 5
WINDOW_SECONDS = 60

request_times = defaultdict(list)


@app.get("/")
def root():
    logger.info("GET /")
    return {"message": "Triage MVP is running"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    logger.info(
        "New triage request | client_id=%s | channel=%s",
        request.client_id,
        request.channel,
    )

    now = time()

    request_times[request.client_id] = [
        timestamp
        for timestamp in request_times[request.client_id]
        if now - timestamp < WINDOW_SECONDS
    ]

    if len(request_times[request.client_id]) >= RATE_LIMIT:
        logger.warning(
            "Rate limit exceeded | client_id=%s",
            request.client_id,
        )

        raise HTTPException(
            status_code=429,
            detail="Слишком много запросов. Попробуйте позже.",
        )

    request_times[request.client_id].append(now)

    try:
        result = triage_with_llm(request.text)

        response = TriageResponse(
            category=result["category"],
            draft_reply=result["draft_reply"],
            confidence=result["confidence"],
            escalate=result["escalate"],
        )

        save_ticket(
            text=request.text,
            channel=request.channel,
            client_id=request.client_id,
            category=response.category,
            draft_reply=response.draft_reply,
            confidence=response.confidence,
            escalate=response.escalate,
        )

        logger.info(
            "Triage completed | client_id=%s | category=%s | confidence=%s | escalate=%s",
            request.client_id,
            response.category,
            response.confidence,
            response.escalate,
        )

        return response

    except Exception as error:
        logger.error(
            "LLM error | client_id=%s | error=%s",
            request.client_id,
            error,
        )

        response = TriageResponse(
            category="other",
            draft_reply="Передано оператору.",
            confidence="low",
            escalate=True,
        )

        save_ticket(
            text=request.text,
            channel=request.channel,
            client_id=request.client_id,
            category=response.category,
            draft_reply=response.draft_reply,
            confidence=response.confidence,
            escalate=response.escalate,
            error=str(error),
        )

        logger.warning(
            "Fallback response returned | client_id=%s",
            request.client_id,
        )

        return response