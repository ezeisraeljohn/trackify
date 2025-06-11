from sqlmodel import SQLModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class Transaction(SQLModel):
    id: UUID
    account_id: UUID
    user_id: UUID
    transaction_id: str
    amount: float
    currency: str
    category: Optional[str]
    transaction_type: str
    raw_description: Optional[str] = None
    normalized_description: Optional[str] = None
    transaction_date: date
    created_at: datetime
    updated_at: datetime


class TransactionReturnDetails(SQLModel):
    success: bool = True
    status: str
    message: str
    data: Transaction | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Transaction details retrieved successfully",
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "123e4567-e89b-12d3-a456-426614174001",
                    "account_id": "123e4567-e89b-12d3-a456-426614174002",
                    "transaction_id": "txn_1234567890",
                    "amount": 100.0,
                    "currency": "USD",
                    "category": "Services",
                    "transaction_type": "debit",
                    "raw_description": "Payment for services",
                    "normalized_description": "Payment for services",
                    "transaction_date": "2023-10-01T12:00:00Z",
                    "created_at": "2023-10-01T12:00:00Z",
                    "updated_at": "2023-10-01T12:00:00Z",
                },
            }
        }


class TransactionReturnList(SQLModel):
    success: bool = True
    status: str
    message: str
    data: list[Transaction] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Transactions retrieved successfully",
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174001",
                        "account_id": "123e4567-e89b-12d3-a456-426614174002",
                        "transaction_id": "txn_1234567890",
                        "amount": 100.0,
                        "currency": "USD",
                        "category": "Services",
                        "transaction_type": "debit",
                        "raw_description": "Payment for services",
                        "normalized_description": "Payment for services",
                        "transaction_date": "2023-10-01T12:00:00Z",
                        "created_at": "2023-10-01T12:00:00Z",
                        "updated_at": "2023-10-01T12:00:00Z",
                    },
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "user_id": "123e4567-e89b-12d3-a456-426614174001",
                        "account_id": "123e4567-e89b-12d3-a456-426614174002",
                        "transaction_id": "txn_0987654321",
                        "amount": 50.0,
                        "currency": "USD",
                        "category": "Groceries",
                        "transaction_type": "credit",
                        "raw_description": "Grocery shopping",
                        "normalized_description": "Grocery shopping",
                        "transaction_date": "2023-10-02T12:00:00Z",
                        "created_at": "2023-10-02T12:00:00Z",
                        "updated_at": "2023-10-02T12:00:00Z",
                    },
                ],
            }
        }


class TransactionSyncResponse(SQLModel):
    success: bool = True
    status: str
    message: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Transactions synced successfully.",
            }
        }
