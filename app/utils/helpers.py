import random
import string
from passlib.context import CryptContext
from app.core import settings
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp(length: int = 6) -> str:
    """
    Create a random OTP of specified length.
    Default length is 6.
    """
    if settings.ENV == "test" or settings.ENV == "development":
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


def apply_mask(number: str, show_last=4, mask_char="*") -> str:
    """
    Mask the account number except for the last few characters.
        :param account_number: The account number to mask.
        :param show_last: Number of characters to show at the end of the account number.
        :param mask_char: Character to use for masking.
        :return: Masked account number.
    """
    if not number or len(number) <= show_last:
        return number
    masked_part = mask_char * (len(number) - show_last)
    visible_part = number[-show_last:]
    return masked_part + visible_part


def hash_email(input_string: str) -> str:
    """
    Hash a string using SHA-256.
    :param input_string: The string to hash.
    :return: Hashed string in hexadecimal format.
    """
    return hashlib.sha256(input_string.lower().strip().encode()).hexdigest()
