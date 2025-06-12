from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlmodel import Session
from app.db.session import get_session
from app.services.mono_client import (
    exchange_code_for_token,
    fetch_account_details,
)
from typing import Annotated
from uuid import uuid4
from datetime import datetime
from app.api.deps import verified_user
from app.models import User, LinkedAccount
from app.crud import get_linked_accounts_by_user_id
from app.services.security import SecurityService
from app.schemas import LinkedAccountReturnDetails, LinkedAccountReturnList, AccountCode
from app.utils.logger import logger
from app.utils.helpers import apply_mask
from app.core import settings

security = SecurityService()


router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.post("/link", response_model=LinkedAccountReturnDetails, status_code=201)
async def link_account(
    code: Annotated[AccountCode, Body(description="Authorization code from Mono")],
    session: Session = Depends(get_session),
    user: User = Depends(verified_user),
):
    """
    Link a Mono account to a user.
    """
    try:
        # Extract and validate the authorization code
        auth_code = code.code
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
        account_data = account_details.get("data", {})

        encrypted_provider_account_id = security.encrypt(data=account_id)
        encrypted_provider_account_balance = security.encrypt(
            data=account_data.get("account", {}).get("balance")
        )
        encrypted_account_name = security.encrypt(
            data=account_data.get("account", {}).get("name")
        )
        encrypted_account_number = security.encrypt(
            data=account_data.get("account", {}).get("account_number")
        )
        # Create or update the linked account in the database
        linked_account = LinkedAccount(
            id=uuid4(),
            user_id=user.id,
            provider_account_id=encrypted_provider_account_id,
            provider="mono",
            account_type=account_data.get("account", {}).get("type"),
            account_name=encrypted_account_name,
            balance=encrypted_provider_account_balance,
            account_number=encrypted_account_number,
            institution=account_data.get("account", {}).get("institution"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(linked_account)
        session.commit()
        session.refresh(linked_account)

        # decrypt sensitive fields for the response
        linked_account.provider_account_id = security.decrypt(
            linked_account.provider_account_id
        )
        linked_account.balance = security.decrypt(linked_account.balance)
        linked_account.account_name = security.decrypt(
            linked_account.account_name,
        )
        linked_account.account_number = security.decrypt(
            linked_account.account_number,
        )
        del linked_account.provider_account_id
        masked_account_number = apply_mask(linked_account.account_number)
        linked_account.account_number = masked_account_number
        # Return the linked account details
        linked_account_response = LinkedAccountReturnDetails(
            success=True,
            status=str(status.HTTP_201_CREATED),
            message="Account linked successfully",
            data=linked_account,
        )
        return linked_account_response
    except HTTPException:
        raise
    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error linking account: {e}")
        else:
            logger.error(f"Error linking account:")
        raise HTTPException(status_code=400, detail="Internal server error")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_linked_accounts(
    db: Session = Depends(get_session),
    user: User = Depends(verified_user),
):
    try:
        linked_accounts = get_linked_accounts_by_user_id(db=db, user_id=user.id)
        decrypted_linked_accounts = []
        for account in linked_accounts:
            # Decrypt sensitive fields
            account.provider_account_id = security.decrypt(account.provider_account_id)
            account.balance = security.decrypt(account.balance)
            account.account_name = security.decrypt(account.account_name)
            account.account_number = security.decrypt(account.account_number)
            del account.provider_account_id
            masked_account_number = apply_mask(account.account_number)
            account.account_number = masked_account_number
            decrypted_linked_accounts.append(account)

        linked_accounts_response = LinkedAccountReturnList(
            success=True,
            status=str(status.HTTP_200_OK),
            message="Linked accounts retrieved successfully",
            data=decrypted_linked_accounts,
        )

        return linked_accounts_response
    except HTTPException:
        raise

    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error fetching linked accounts: {e}")
        else:
            logger.error(f"Error fetching linked accounts:")
        raise HTTPException(status_code=500, detail=str(e))
