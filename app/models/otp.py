from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime


class OTP(SQLModel, table=True):
    """
    Represents a One-Time Password (OTP) for user authentication.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    otp_code: str = Field(nullable=False)
    is_used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    user: "User" = Relationship(back_populates="otps")
