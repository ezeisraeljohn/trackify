from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from uuid import uuid4, UUID
from typing import Optional, Dict, Any
from datetime import datetime


class LinkedAccount(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    provider: str = Field(default="mono", max_length=50)
    provider_account_id: str
    account_name: str
    account_type: str
    account_number: Optional[str] = None
    currency: str = Field(default="NGN", max_length=3)
    balance: str
    institution: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "provider_account_id": "acc_1234567890",
                "account_name": "John Doe",
                "account_type": "savings",
                "account_number": "1234567890",
                "currency": "NGN",
                "balance": "10000.00",
                "institution": {"name": "Bank Name", "logo": "bank_logo.png"},
            }
        }
