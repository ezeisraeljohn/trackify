from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.services.llm_assistant import summarize_user_spending
from app.models.user import User
from app.api.deps import get_current_user
from uuid import UUID
from app.schemas import LLMResponse, LLMQuery

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])


@router.post("/query", response_model=LLMResponse)
def ask_ai(
    user_message: LLMQuery,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> LLMResponse:
    """
    Ask the AI assistant a question based on the user's transactions.

    Args:
        user_message (dict): The user's message containing their question.
        user (User): The current user.
        session (Session): The database session.

    Returns:
        LLMResponse: The response from the AI assistant.
    """
    if not user_message or not hasattr(user_message, "message"):
        raise HTTPException(status_code=400, detail="Invalid request format")

    try:
        response_text = summarize_user_spending(
            user,
            user_message.message,
            session,
        )
        return LLMResponse(
            success=True,
            status=200,
            message="AI response generated successfully",
            reply=response_text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
