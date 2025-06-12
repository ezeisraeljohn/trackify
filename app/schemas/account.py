from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any


class LinkedAccountDetail(SQLModel):
    id: UUID
    user_id: UUID
    provider: str
    account_type: str
    account_name: str
    balance: str
    account_number: str | None = None
    institution: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class LinkedAccountReturnDetails(SQLModel):
    success: bool = Field(default=True)
    status: str
    message: str
    data: LinkedAccountDetail | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "success",
                "message": "Linked account details retrieved successfully",
                "data": {
                    "id": UUID,
                    "user_id": UUID,
                    "provider": "mono",
                    "account_type": "savings",
                    "account_name": "John Doe Savings Account",
                    "balance": "1000.00",
                    "account_number": "1234567890",
                    "institution": {
                        
                    }
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                },
            }
        }


class LinkedAccountReturnList(SQLModel):
    success: bool = Field(default=True)
    status: str
    message: str
    data: list[LinkedAccountDetail] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Linked accounts retrieved successfully",
                "data": [
                    {
                        "id": UUID,
                        "user_id": UUID,
                        "provider": "mono",
                        "account_type": "savings",
                        "account_name": "John Doe Savings Account",
                        "balance": "1000.00",
                        "account_number": "1234567890",
                        "institution": {"name": "Mono Bank"},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                ],
            }
        }


class AccountCode(SQLModel):
    code: str
