"""
Chat endpoint.

Handles conversational AI requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.models.chat_request import ChatRequest
from src.api.models.chat_response import ChatResponse, RecommendationModel
from src.api.dependencies import get_orchestrator
from src.orchestrator.engine.conversation_orchestrator import ConversationOrchestrator
from src.orchestrator.domain.execution_context import ConversationMessage
from src.conversation.intent.domain.intent_types import IntentType
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    orchestrator: ConversationOrchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    """
    Process conversational AI request.
    
    This endpoint is extremely thin - ALL business logic is in the orchestrator.
    
    Args:
        request: Chat request with messages
        orchestrator: Injected orchestrator instance
    
    Returns:
        Chat response with reply, recommendations, and end flag
    
    Raises:
        HTTPException: On internal errors
    """
    try:
        # Extract current message and history
        current_message = request.get_current_message()
        history_messages = request.get_history()
        
        # Convert to orchestrator format
        conversation_history = [
            ConversationMessage(role=msg.role, content=msg.content)
            for msg in history_messages
        ]
        
        logger.info(f"Processing chat request: {len(history_messages)} history messages")
        
        # Execute orchestrator
        result = await orchestrator.execute(
            user_message=current_message,
            conversation_history=conversation_history,
            session_id="",  # Session management can be added later
        )
        
        # Check if execution succeeded
        if not result.success:
            logger.error("Orchestrator execution failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process request",
            )
        
        # Extract recommendations if present
        recommendations = []
        if result.recommendation_result and result.recommendation_result.recommendations:
            for rec in result.recommendation_result.recommendations[:10]:  # Max 10
                recommendations.append(
                    RecommendationModel(
                        title=rec.assessment_name,
                        url=rec.official_url,
                        description=f"{rec.category} - {rec.test_type}. {rec.recommendation_reason}",
                        competencies=rec.matching_competencies,
                        duration=rec.duration_minutes,
                    )
                )
        
        # Determine if conversation ended
        end_of_conversation = False
        if result.intent_result:
            # Conversation ends on: COMPLETION, REFUSAL, or being BLOCKED
            if result.intent_result.primary_intent in [
                IntentType.COMPLETION,
                IntentType.REFUSAL,
            ]:
                end_of_conversation = True
            
            # Also end if blocked by guardrails
            if result.guardrail_input_result and result.guardrail_input_result.should_block():
                end_of_conversation = True
        
        # Build response
        response = ChatResponse(
            reply=result.response,
            recommendations=recommendations,
            end_of_conversation=end_of_conversation,
        )
        
        logger.info(f"Chat request completed: {len(recommendations)} recommendations")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Log and return generic error (never expose internals)
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request",
        )
