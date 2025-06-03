from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from pydantic import EmailStr
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    first_name: str
    last_name: str
    hashed_password: str
    is_email_verified: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    linked_accounts: list["LinkedAccount"] = Relationship(back_populates="user")
    otps: list["OTP"] = Relationship(back_populates="user")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": UUID,
                "email": EmailStr,
                "first_name": str,
                "last_name": str,
                "created_at": datetime,
                "updated_at": datetime,
            }
        }
