from sqlmodel import SQLModel, Field, Relationship
from ..models import User
from pydantic import EmailStr
from datetime import datetime
from uuid import UUID


class UserCreate(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
    first_name: str
    last_name: str


class UserUpdate(SQLModel):
    first_name: str
    last_name: str


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
