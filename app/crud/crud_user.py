from sqlmodel import Session
from app.models import User
from app.schemas import UserCreate
from sqlmodel import select
from app.api.deps import password_hash


def insert_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.
    """
    hashed_password = password_hash(user.hashed_password)
    user.hashed_password = hashed_password
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
