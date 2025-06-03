from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.orm.session import Session
from app.api.deps import get_user_by_email
from app.crud import insert_user
from app.schemas import UserCreate, UserReturnDetails, Token
from app.db.session import get_session
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from ...deps import authenticate_user, create_access_token
from datetime import timedelta
import os
from app.core import settings


router = APIRouter(prefix="/api/v1/users", tags=["Users"])
