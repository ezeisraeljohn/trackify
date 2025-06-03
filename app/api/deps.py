from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlmodel.orm.session import Session
from app.models import User
from sqlmodel import select
from app.db.session import get_session
from passlib.context import CryptContext
from app.core import settings
import jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def password_hash(password: str) -> str:
    """
    Hash a password.
    """
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get a user by email.
    """
    user = db.exec(select(User).where(User.email == email)).first()
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    """
    user = get_user_by_email(db=db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM
    if not secret_key or not algorithm:
        raise RuntimeError("SECRET_KEY and ALGORITHM environment variables must be set")
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
) -> User:
    """
    Get the current user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        secret_key = settings.SECRET_KEY
        algorithm = settings.ALGORITHM
        if not secret_key or not algorithm:
            raise RuntimeError(
                "SECRET_KEY and ALGORITHM environment variables must be set"
            )
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception
    return user


def verified_user(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> User:
    """
    Ensure the user is verified.
    """
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User email is not verified",
        )
    return user
