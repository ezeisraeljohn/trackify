from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime


class Insight(SQLModel, table=True):
    """The insight table"""

    __tablename__ = "insights"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    message: str
    type: str = Field(default="info")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
