import os
from dotenv import load_dotenv
from google.genai import types
from app.models import Transaction
from datetime import datetime, timedelta
from sqlmodel import UUID, select
from sqlmodel.orm.session import Session
from app.models.user import User
from google import genai

# Load environment variables from .env file
load_dotenv()


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def summarize_user_spending(
    user: User,
    user_message: str,
    session: Session,
) -> str:
    """
    Summarize user spending based on their transactions.

    Args:
        transactions (list[Transaction]): List of transactions for the user.
        user_id (UUID): The ID of the user.

    Returns:
        str: A summary of the user's spending.
    """
    last_30_days = datetime.today() - timedelta(days=30)
    txs = select(Transaction).where(
        Transaction.user_id == user.id,
        Transaction.transaction_date >= last_30_days,
    )
    transactions = session.exec(txs).all()

    summary = ""
    for tx in transactions:
        summary += (
            f"Transaction ID: {tx.transaction_id}, |"
            f"Date: {tx.transaction_date.strftime('%Y-%m-%d')}, |"
            f"Amount: {tx.amount / 100:.2f} {tx.currency}, |"
            f"type: {tx.transaction_type}, |"
            f"category: {tx.category}, |"
            f"Description: {tx.normalized_description} | \n"
        )
    user_name = (
        f"{user.first_name} {user.last_name}" if user is not None else "Unknown User"
    )
    prompt = f"""
    You are a financial assistant for a user named {user_name}.
    User's recent transactions (last 30 days):
    {summary}
User's question: {user_message}

Answer clearly and helpfully in 2 to 3 sentences.

    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return (
        response.text.strip()
        if response and response.text
        else "No response generated."
    )
