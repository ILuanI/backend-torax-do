from typing import Optional
from pydantic import BaseModel, Field

class AiChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None

class AiChatResponse(BaseModel):
    answer: str
    model: str
    usage: dict | None = None
