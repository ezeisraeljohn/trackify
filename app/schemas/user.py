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

    class Config:
        orm_mode = True
