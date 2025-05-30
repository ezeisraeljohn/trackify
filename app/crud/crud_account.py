from sqlmodel.orm.session import Session
from app.models import LinkedAccount
from sqlmodel import select, UUID


def get_linked_account_by_id(db: Session, account_id: int) -> LinkedAccount | None:
    """
    Get a linked account by its ID.
    """
    statement = select(LinkedAccount).where(LinkedAccount.id == account_id)
    result = db.exec(statement).first()
    return result


def get_linked_accounts_by_user_id(
    db: Session,
    user_id: UUID,
) -> list[LinkedAccount]:
    """
    Get all linked accounts for a user by their user ID.
    """
    statement = select(LinkedAccount).where(LinkedAccount.user_id == user_id)
    result = db.exec(statement).all()
    return list(result)
