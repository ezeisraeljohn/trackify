from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.orm.session import Session
from app.db.session import get_session
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import (
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_current_user,
)
from datetime import timedelta
import os
from app.core import settings
from app.schemas import (
    UserCreate,
    UserCreateResponse,
    Token,
    VerifyEmailBody,
    UserInternalCreate,
)
from app.crud import insert_user, create_otp, verify_otp
from app.jobs.email_jobs.email_jobs import send_verification_email
from typing import Annotated
from fastapi import Body
from app.models import User
from app.services import security
from app.utils.helpers import hash_email
from app.utils.logger import logger


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
            data={"sub": user.encrypted_email},
            expires_delta=timedelta(
                minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            ),  # Token expiration time in seconds
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(os.getenv(str(settings.ACCESS_TOKEN_EXPIRE_MINUTES), "30"))
            * 60,  # Convert to seconds
        )

    except HTTPException:
        raise

    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error during login: {e}")
        else:
            logger.error("Error during login")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register", response_model=UserCreateResponse, status_code=201)
async def create_user(
    user: Annotated[UserCreate, Body()],
    db: Session = Depends(get_session),
) -> UserCreateResponse | None:
    """
    Create a new user.
    """

    try:
        db_user = get_user_by_email(db=db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        user_internal = UserInternalCreate(
            email=user.email,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            encrypted_email=security.encrypt(data=user.email),
            hashed_email=hash_email(user.email),  # Hash the email for storage
        )
        data = insert_user(db=db, user=user_internal)
        # Create OTP for the new user
        otp = create_otp(db=db, user_id=data.id)
        if not otp:
            raise HTTPException(status_code=500, detail="Internal server error")
        body = {
            "user_name": f"{user.first_name} {user.last_name}",
            "code": otp,
        }
        send_verification_email.delay(user.email, "Email Verification", body=body)
        access_token = create_access_token(
            data={"sub": user_internal.encrypted_email},
            expires_delta=timedelta(
                minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            ),  # Token expiration time in seconds
        )
        return UserCreateResponse(
            status="success",
            message="User created successfully",
            data={
                "message": "Please check your email for verification code.",
                "access_token": access_token,
            },
        )
    except HTTPException:
        raise

    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error creating user: {e}")
        else:
            logger.error("Error creating user")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-email", status_code=200)
def verify_email(
    data: Annotated[VerifyEmailBody, Body()],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict:
    """
    Verify user email with OTP.
    """
    try:

        if user.is_email_verified:
            raise HTTPException(status_code=400, detail="User is already verified")

        # Verify the OTP
        is_otp_valid = verify_otp(db=db, user_id=user.id, otp_code=data.otp_code)
        if not is_otp_valid:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Update user email verification status
        user.is_email_verified = True
        db.add(user)
        db.commit()

        return {"status": "success", "message": "Email verified successfully"}

    except HTTPException:
        raise

    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error verifying email: {e}")
        else:
            logger.error("Error verifying email")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/resend-verification-email", status_code=200)
def resend_verification_email(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict:
    """
    Resend verification email to the user.
    """
    try:
        if user.is_email_verified:
            raise HTTPException(status_code=400, detail="User is already verified")

        # Create a new OTP for the user
        otp = create_otp(db=db, user_id=user.id)
        if not otp:
            raise HTTPException(status_code=500, detail="Internal server error")

        body = {
            "user_name": f"{user.first_name} {user.last_name}",
            "code": otp,
        }
        decrypted_email = security.decrypt(encrypted_data=user.encrypted_email)
        send_verification_email.delay(
            email=decrypted_email, subject="Email Verification", body=body
        )

        return {
            "status": "success",
            "message": "Verification email resent successfully",
        }
    except HTTPException:
        raise

    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error resending verification email: {e}")
        else:
            logger.error("Error resending verification email")
        raise HTTPException(status_code=500, detail="Internal server error")
