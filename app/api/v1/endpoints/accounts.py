from fastapi import APIRouter, Depends, HTTPException, requests
from sqlmodel import Session
from app.db.session import get_session
from app.services.mono_client import (
    exchange_code_for_token,
    fetch_account_details,
)
from ....models import LinkedAccount
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.post("/link")
async def link_account(code: dict, session: Session = Depends(get_session)):
    """
    Link a Mono account to a user.
    """
    try:
        print(code.get("code"))
        # Exchange the authorization code for a token
        token_response = await exchange_code_for_token(code.get("code"))
        account_id = token_response["data"]["id"]

        # Fetch account details
        account_details = await fetch_account_details(account_id)
        print(account_details)

        # Create or update the linked account in the database
        linked_account = LinkedAccount(
            id=uuid4(),
            user_id=uuid4(),  # Replace with the actual user ID from your authentication system
            provider_account_id=account_id,
            provider="mono",
            account_type=account_details.get("data").get("account").get("type"),
            account_name=account_details.get("data").get("account").get("name"),
            balance=account_details.get("data").get("account").get("balance"),
            account_number=account_details.get("data")
            .get("account")
            .get("account_number"),
            institution=account_details.get("data").get("account").get("institution"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(linked_account)
        session.commit()
        session.refresh(linked_account)

        return {"message": "Account linked successfully", "data": linked_account}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
