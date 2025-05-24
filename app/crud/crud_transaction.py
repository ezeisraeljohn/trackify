from sqlmodel.orm.session import Session
from app.models import Transaction
from sqlmodel import select


def get_transaction_by_id(db: Session, id: int) -> Transaction | None:
    """
    Get a transaction by its ID.
    """
    statement = select(Transaction).where(Transaction.id == id)
    result = db.exec(statement).first()
    return result


def get_transactions(db: Session, account_id: str) -> list[Transaction]:
    """
    Get all transactions for a user by their user ID.
    """
    statement = select(Transaction).where(Transaction.account_id == account_id)
    result = db.exec(statement).all()
    return list(result)


def get_transaction_by_transaction_id(
    db: Session, transaction_id: str
) -> Transaction | None:
    """
    Get a transaction by its transaction ID.
    """
    statement = select(Transaction).where(Transaction.transaction_id == transaction_id)
    result = db.exec(statement).first()
    return result
