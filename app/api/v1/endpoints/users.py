from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.orm.session import Session
from app.api.deps import get_user_by_email
from app.crud import insert_user
from app.schemas import UserCreate, UserReturnDetails, Token
from app.db.session import get_session
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import authenticate_user, create_access_token
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/", response_model=UserReturnDetails, status_code=201)
def create_user(
    user: UserCreate, db: Session = Depends(get_session)
) -> UserReturnDetails | None:
    """
    Create a new user.
    """

    try:
        db_user = get_user_by_email(db=db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        value = insert_user(db=db, user=user)
        return UserReturnDetails(
            status="success", message="User created successfully", data=value
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
