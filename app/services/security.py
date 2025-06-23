from cryptography.fernet import Fernet
from app.utils.logger import logger
from app.core import settings
from typing import Union


class SecurityService:
    def __init__(self):
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not set in settings")
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt(self, data: Union[str, int, float]) -> str:
        """
        Encrypt the given data using the secret key.
        """
        if not data:
            raise ValueError("Data to encrypt cannot be empty")
        return self.cipher.encrypt(str(data).encode()).decode()

    def decrypt(self, encrypted_data: str | None) -> str | None:
        """
        Decrypt the given encrypted data using the secret key.
        """
        if not encrypted_data:
            return
        return self.cipher.decrypt(encrypted_data.encode()).decode()
