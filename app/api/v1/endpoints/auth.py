from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.orm.session import Session
from app.schemas import Token
from app.db.session import get_session
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import authenticate_user, create_access_token
from datetime import timedelta
import os
from dotenv import load_dotenv
from app.schemas import UserCreate, UserReturnDetails
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import authenticate_user, create_access_token
from datetime import timedelta
from app.api.deps import get_user_by_email
from app.crud import insert_user

load_dotenv()

router = APIRouter(prefix="/api/v1/auth", tags=["Users"])


@router.post("/login", response_model=Token, status_code=200)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)
) -> Token | None:
    """
    Login a user.
    """
    try:
        user = authenticate_user(
            db=db, email=form_data.username, password=form_data.password
        )
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(
                minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            ),  # Token expiration time in seconds
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            * 60,  # Convert to seconds
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register", response_model=UserReturnDetails, status_code=201)
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
