from fastapi import APIRouter

from app.schemas.ai import AiChatRequest, AiChatResponse
from app.services.digital_ocean_ai_service import digital_ocean_ai_service

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/chat", response_model=AiChatResponse)
async def chat_with_ai(payload: AiChatRequest):
    result = await digital_ocean_ai_service.chat(
        prompt=payload.prompt,
        system_prompt=payload.system_prompt,
    )
    return result
