from typing import Literal

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    channel: Literal["email", "form", "chat"]
    client_id: str


class TriageResponse(BaseModel):
    category: Literal["billing", "support", "complaint", "other"]
    draft_reply: str = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]
    escalate: bool