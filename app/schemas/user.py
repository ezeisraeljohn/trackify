from sqlmodel import SQLModel, Field
from ..models import User
from pydantic import EmailStr
from datetime import datetime
from uuid import UUID
from typing import Dict


class UserCreate(SQLModel):
    email: EmailStr = Field(nullable=False)
    hashed_password: str
    first_name: str
    last_name: str


class UserInternalCreate(UserCreate, SQLModel):
    encrypted_email: str
    hashed_email: str


class UserUpdate(SQLModel):
    first_name: str
    last_name: str


class UserCreateResponse(SQLModel):
    status: str
    message: str
    data: Dict[str, str]


class UserReturnDetails(SQLModel):
    status: str
    message: str
    data: User | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "User created successfully",
                "data": {
                    "id": UUID,
                    "email": EmailStr,
                    "first_name": str,
                    "last_name": str,
                    "created_at": datetime,
                    "updated_at": datetime,
                },
            }
        }


class Token(SQLModel):
    access_token: str
    token_type: str
    expires_in: int  # Default expiration time in seconds


class VerifyEmailBody(SQLModel):
    email: EmailStr
    otp_code: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"email": "example@example.com", "otp_code": "123456"}
        }


class EmailVerificationResponse(SQLModel):
    status: str
    message: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Email verified successfully",
                "data": {},
            }
        }
