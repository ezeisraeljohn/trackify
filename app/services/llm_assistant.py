from app.core import settings
from google.genai import types
from app.models import Transaction
from datetime import datetime, timedelta
from sqlmodel import UUID, select
from sqlmodel.orm.session import Session
from app.models.user import User
from google import genai
from app.langchain.sql_toolkit import graph, config


client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def summarize_user_spending(
    user: User,
    user_message: str,
    session: Session,
) -> str:
    """
    Returns responses to users requets.

    Args:
        transactions (list[Transaction]): List of transactions for the user.
        user_id (UUID): The ID of the user.

    Returns:
        str: The AI Answer.
    """
    result = graph.invoke({"question": user_message, "id": str(user.id)}, config=config)
    if result and "answer" in result:
        return result["answer"]
    else:
        raise ValueError("No answer found in the result from the AI assistant.")
