from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlmodel import Session
from app.db.session import get_session
from app.services.mono_client import (
    exchange_code_for_token,
    fetch_account_details,
)
from typing import Annotated
from ....models import LinkedAccount
from uuid import uuid4
from datetime import datetime
from app.api.deps import get_current_user
from app.models import User
from app.crud import get_linked_accounts_by_user_id


router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.post("/link", status_code=201)
async def link_account(
    code: Annotated[dict, Body(description="Authorization code from Mono")],
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Link a Mono account to a user.
    """
    try:
        # Extract and validate the authorization code
        auth_code = code.get("code")
        if not isinstance(auth_code, str) or not auth_code:
            raise HTTPException(
                status_code=400,
                detail="Authorization code is required and must be a string",
            )
        # Exchange the authorization code for a token
        token_response = await exchange_code_for_token(auth_code)
        account_id = token_response["data"]["id"]

        # Fetch account details
        account_details = await fetch_account_details(account_id)

        # Create or update the linked account in the database
        linked_account = LinkedAccount(
            id=uuid4(),
            user_id=user.id,
            provider_account_id=account_id,
            provider="mono",
            account_type=account_details.get("data", {}).get("account", {}).get("type"),
            account_name=account_details.get("data", {}).get("account", {}).get("name"),
            balance=account_details.get("data", {}).get("account", {}).get("balance"),
            account_number=account_details.get("data", {})
            .get("account", {})
            .get("account_number"),
            institution=account_details.get("data", {})
            .get("account", {})
            .get("institution"),
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


@router.get("/", status_code=status.HTTP_200_OK)
async def get_linked_accounts(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        linked_accounts = get_linked_accounts_by_user_id(db=db, user_id=user.id)
        return {
            "status": status.HTTP_200_OK,
            "message": "Account linked successfully",
            "data": linked_accounts,
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
