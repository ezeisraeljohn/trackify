from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.orm.session import Session
from app.db.session import get_session
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import authenticate_user, create_access_token, get_user_by_email
from datetime import timedelta
import os
from dotenv import load_dotenv
from app.schemas import UserCreate, UserCreateResponse, Token
from app.crud import insert_user, create_otp
from app.services.email_setup import EmailService
from app.jobs.email_jobs import send_verification_email

load_dotenv()
email_service = EmailService()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, status_code=200)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
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


@router.post("/register", response_model=UserCreateResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_session),
) -> UserCreateResponse | None:
    """
    Create a new user.
    """

    try:
        db_user = get_user_by_email(db=db, email=user.email)
        print(f"Checking if user exists: {db_user}")
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        data = insert_user(db=db, user=user)

        # Create OTP for the new user
        otp = create_otp(db=db, user_id=data.id)
        print(f"OTP for user {data.email}: {otp}")
        if not otp:
            raise HTTPException(status_code=500, detail="Internal server error")
        body = {
            "user_name": f"{user.first_name} {user.last_name}",
            "code": otp,
        }
        send_verification_email.delay(user.email, "Email Verification", body=body)
        return UserCreateResponse(
            status="success",
            message="User created successfully",
            data={"message": "Please check your email for verification."},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


@router.post("/verify-email", status_code=200)
def verify_email(
    email: str,
    otp: str,
    db: Session = Depends(get_session),
) -> dict:
    """
    Verify user email with OTP.
    """
    try:
        user = get_user_by_email(db=db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_email_verified:
            raise HTTPException(status_code=400, detail="User is already verified")

        user.is_email_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"status": "success", "message": "Email verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))
