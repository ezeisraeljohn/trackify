from sqlmodel import Session
from app.models import User
from app.schemas import UserInternalCreate
from sqlmodel import select
from app.api.deps import password_hash
from app.services import email_service, security
from app.utils.helpers import hash_email


def insert_user(db: Session, user: UserInternalCreate) -> User:
    """
    Create a new user in the database.
    """
    user.hashed_password = password_hash(user.hashed_password)
    db_user = User.model_validate(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return_message = db_user
    return return_message


def get_unverified_users(db: Session):
    """
    Retrieve all unverified users from the database.
    """
    statement = select(User).where(User.is_email_verified == False)
    results = db.exec(statement)
    return results.all()
