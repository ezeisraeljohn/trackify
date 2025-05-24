import httpx
import os
from dotenv import load_dotenv

load_dotenv()
base_URL = os.getenv("MONO_BASE_URL")
secret_key = os.getenv("MONO_SECRET_KEY")


async def exchange_code_for_token(code: str) -> dict:
    """Exchange the authorization code for Users ID"""

    url = f"{base_URL}/accounts/auth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "mono-sec-key": secret_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data={"code": code})
        response.raise_for_status()
        return response.json()


async def fetch_account_details(account_id: str) -> dict:
    """Fetch account details using the Mono API"""
    url = f"{base_URL}/accounts/{account_id}"
    headers = {
        "accept": "application/json",
        "mono-sec-key": secret_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_transactions(account_id: str) -> dict:
    """Fetch transactions using the Mono API"""
    url = f"{base_URL}/accounts/{account_id}/transactions"
    headers = {
        "accept": "application/json",
        "mono-sec-key": secret_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(response.json())
        response.raise_for_status()
        return response.json()
