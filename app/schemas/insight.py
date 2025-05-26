from sqlmodel import SQLModel
from typing import List
from ..models import Insight


class InsightGenerateReturnList(SQLModel):
    """Schema for returning a list of generated insights."""

    success: bool  # Indicates if the operation was successful
    message: str  # Message describing the result of the operation
    status: int  # Status of the operation
    insights: List[Insight]  # List of generated insights

    class Config:
        """Configuration for the schema."""

        from_attributes = True
