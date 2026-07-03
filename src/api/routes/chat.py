"""Chat endpoint."""

from fastapi import APIRouter, Depends

from src.conversation.schemas.conversation_schemas import ChatRequestSchema, ChatResponseSchema
from src.conversation.application.orchestrator import ConversationOrchestrator
from src.conversation.dependencies import get_conversation_orchestrator

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponseSchema)
async def chat(
    request: ChatRequestSchema,
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator)
) -> ChatResponseSchema:
    """Process conversation and return response."""
    pass
