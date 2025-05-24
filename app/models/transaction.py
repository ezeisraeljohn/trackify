from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import Optional, Type
from datetime import date, datetime


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="linked_accounts.id")
    user_id: UUID = Field(foreign_key="users.id")
    transaction_id: Type[str]
    amount: float
    currency: Type[str]
    category: Optional[str] = None
    transaction_type: str = Field(default="debit", max_length=10)
    raw_description: Optional[str] = None
    normalized_description: Optional[str] = None
    transaction_date: date
    account: Optional["LinkedAccount"] = Relationship(back_populates="transactions")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
