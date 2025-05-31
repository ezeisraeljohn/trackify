from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.session import get_session
from app.services.insights import generate_insights
from app.models.insight import Insight
from uuid import UUID
from app.api.deps import get_current_user
from app.models import User
from ....schemas import InsightGenerateReturnList
from datetime import datetime, timedelta


router = APIRouter(prefix="/api/v1/insights", tags=["Insights"])


@router.post("/generate", response_model=InsightGenerateReturnList)
async def generate_insights_endpoint(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> InsightGenerateReturnList:
    """
    Generate insights for the current user based on their transactions.

    Args:
        user (UUID): The ID of the current user.
        session (Session): The database session.

    Returns:
        list[Insight]: A list of generated insights for the user.
    """
    insights = generate_insights(db=session, user_id=user.id)
    for i in insights:
        session.add(i)
    session.commit()
    one_second_ago = datetime.now() - timedelta(seconds=1)
    insights_query = select(Insight).where(
        Insight.user_id == user.id, Insight.created_at >= one_second_ago
    )
    insights = session.exec(insights_query).all()
    return InsightGenerateReturnList(
        success=True,
        status=201,
        message="Insights generated successfully",
        insights=list(insights),
    )


@router.get("/{user_id}", response_model=InsightGenerateReturnList)
async def get_user_insights(
    user_id: UUID,
    session: Session = Depends(get_session),
) -> InsightGenerateReturnList:
    """
    Get all insights for a specific user.

    Args:
        user_id (UUID): The ID of the user to fetch insights for.
        session (Session): The database session.

    Returns:
        InsightGenerateReturnList: A list of insights for the specified user.
    """
    statement = select(Insight).where(Insight.user_id == user_id)
    insights = session.exec(statement).all()
    return InsightGenerateReturnList(
        success=True,
        status=200,
        message="Insights fetched successfully",
        insights=list(insights),
    )
