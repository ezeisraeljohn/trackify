import random
import string
from passlib.context import CryptContext
from app.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp(length: int = 6) -> str:
    """
    Create a random OTP of specified length.
    Default length is 6.
    """
    if settings.ENV == "test" or settings.ENV == "development":
        print("Generating OTP for testing/development environment")
        return "123456"
    characters = string.digits
    otp = "".join(random.choice(characters) for _ in range(length))
    return otp


def hash_otp(otp: str) -> str:
    """
    Hash the OTP using bcrypt.
    """
    return pwd_context.hash(otp)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """
    Verify the plain OTP against the hashed OTP.
    """
    return pwd_context.verify(plain_otp, hashed_otp)
