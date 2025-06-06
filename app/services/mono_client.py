import httpx
import os
from dotenv import load_dotenv
from mono_connect import MonoConnectClient
from app.core import settings

load_dotenv()
secret_key = settings.MONO_SECRET_KEY

client = MonoConnectClient(sec_key=str(secret_key))


async def exchange_code_for_token(code: str) -> dict:
    """Exchange the authorization code for Users ID"""
    if not code:
        raise ValueError("Authorization code is required for token exchange.")
    return client.token_exchange(code=code)


async def fetch_account_details(account_id: str) -> dict:
    """Fetch account details using the Mono API"""
    return client.get_account_details(account_id=account_id)


async def fetch_transactions(account_id: str) -> dict:
    """Fetch transactions using the Mono API"""
    if not account_id:
        raise ValueError("Account ID is required to fetch transactions.")
    return client.get_transactions(account_id=account_id)
