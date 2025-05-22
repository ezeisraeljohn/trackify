from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import User
from app.schemas import UserUpdate, UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.
    """
    db_user = User.model_validate(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
