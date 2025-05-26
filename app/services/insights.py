from sqlmodel import Session, select
from uuid import UUID
from app.models.transaction import Transaction
from app.models.insight import Insight
from datetime import date, timedelta
from collections import defaultdict


def generate_insights(db: Session, user_id: UUID) -> list[Insight]:
    """Generate insights for a user based on their transactions."""
    # Fetch transactions for the user
    today = date.today()
    last_30_days = today - timedelta(days=30)
    statement = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= last_30_days,
    )
    transactions = db.exec(statement).all()

    # Group transactions by category
    insights = []
    total_spent = 0
    spent_by_category = defaultdict(float)
    for tx in transactions:
        amount = tx.amount / 100  # Convert amount from kobo to naira
        total_spent += amount
        if tx.amount > 0:
            spent_by_category[tx.category] += tx.amount

    insights.append(
        Insight(
            user_id=user_id,
            message=f"Total spent in the last 30 days: {total_spent:.2f}",
            type="info",
        )
    )

    # Top category
    if spent_by_category:
        top_category = max(spent_by_category.items(), key=lambda item: item[1])
        tom_cat = top_category[0]
        tom_cat_amount = top_category[1] / 100

        insights.append(
            Insight(
                user_id=user_id,
                message=f"Top category in the last 30 days: "
                f"{tom_cat} with amount {tom_cat_amount:.2f}",
                type="info",
            )
        )

    # Bottom category
    if spent_by_category:
        bottom_category = min(
            spent_by_category.items(),
            key=lambda item: item[1],
        )
        bot_cat = bottom_category[0]
        bot_cat_amount = bottom_category[1] / 100

        insights.append(
            Insight(
                user_id=user_id,
                message=f"Bottom category in the last 30 days: "
                f"{bot_cat} with amount {bot_cat_amount:.2f}",
                type="info",
            )
        )

    # warnings for high spending
    if total_spent > 100000:
        insights.append(
            Insight(
                user_id=user_id,
                message=f"You've spent over 100000 this month."
                f"Consider reviewing your habits.",
                type="warning",
            )
        )

    return insights
