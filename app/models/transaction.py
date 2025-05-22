from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime


class Transaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="linkedaccount.id")
    user_id: UUID = Field(foreign_key="user.id")
    transaction_id: str
    amount: float
    currency: str
    transaction_type: str = Field(default="debit", max_length=10)
    raw_description: Optional[str] = None
    normalized_description: Optional[str] = None
    transaction_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
