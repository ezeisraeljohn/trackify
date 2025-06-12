from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any
from typing import Annotated
from sqlmodel import Session
from app.db.session import get_session
from app.services.mono_client import fetch_transactions
from app.services.normalizer import categorize_transaction, normalize_description
from datetime import datetime
from app.api.deps import verified_user
from app.models import User, Transaction
from app.crud import (
    get_linked_account_by_id,
    get_transactions as transaction_crud,
    get_transaction_by_transaction_id,
)
from app.utils.logger import logger
from app.services import security
from app.core import settings
from app.schemas import (
    TransactionReturnDetails,
    TransactionSyncResponse,
    TransactionReturnList,
)


router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post("/sync", response_model=TransactionSyncResponse, status_code=200)
async def sync_transactions(
    account_id: Annotated[str, Query(description="The account id of the user")],
    session: Session = Depends(get_session),
    user: User = Depends(verified_user),
):
    """Sync transactions for a linked account.
    This endpoint fetches transactions from the Mono API and stores them in the database.
    It is assumed that the account_id is already linked to a user in the database.
    The transactions are fetched using the Mono API and stored in the database.
    The transactions are associated with the linked account using the account_id.

    Args:
        account_id (str): The account ID to sync transactions for.
        session (Session, optional): _description_. Defaults to Depends(get_session).
    """
    try:
        # Check if the account_id is linked to the user
        linked_account = get_linked_account_by_id(
            db=session,
            account_id=account_id,
        )
        if not linked_account or linked_account not in user.linked_accounts:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access"
            )

        provider_account_id = linked_account.provider_account_id

        decrypted_provider_account_id = security.decrypt(
            encrypted_data=provider_account_id
        )
        # Fetch transactions from the Mono API
        transactions_response = await fetch_transactions(decrypted_provider_account_id)
        transactions = transactions_response.get("data", [])

        if not transactions:
            return TransactionSyncResponse(
                success=True, status="200", message="No transactions to sync."
            )

        # Store transactions in the database
        for transaction in transactions:
            transaction["narration"] = normalize_description(
                transaction.get("narration", "")
            )

            # Categorize the transaction
            category = categorize_transaction(transaction.get("narration", ""))

            transaction["category"] = category

            existing_transaction = get_transaction_by_transaction_id(
                db=session,
                transaction_id=transaction.get("id"),
            )

            if existing_transaction:
                continue

            # Create a new transaction object
            date = transaction.get("date")
            new_transaction = Transaction(
                account_id=account_id,
                user_id=user.id,
                transaction_id=transaction.get("id"),
                category=transaction.get("category"),
                transaction_type=transaction.get("type"),
                amount=transaction.get("amount"),
                currency=transaction.get("currency"),
                raw_description=transaction.get("narration"),
                normalized_description=transaction.get("narration"),
                transaction_date=datetime.fromisoformat(
                    date.replace("Z", "+00:00"),
                ),
            )
            session.add(new_transaction)
        session.commit()

        return TransactionSyncResponse(
            success=True,
            status="200",
            message="Transactions synced successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        if settings.DEBUG:
            logger.exception(f"Error syncing transactions: {e}")
        else:
            logger.exception("Error syncing transactions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/", response_model=TransactionReturnList, status_code=200)
async def get_transactions(
    account_id: Annotated[str, Query(description="The account id of the user")],
    session: Session = Depends(get_session),
    user: User = Depends(verified_user),
):
    """Get transactions for a linked account.
    This endpoint fetches transactions from the database for a given linked account.
    The transactions are associated with the linked account using the account_id.

    Args:
        account_id (str): The account ID to fetch transactions for.
        session (Session, optional): _description_. Defaults to Depends(get_session).
    """
    try:
        # Check if the account_id is linked to the user
        linked_account = get_linked_account_by_id(
            db=session,
            account_id=account_id,
        )
        if not linked_account or linked_account not in user.linked_accounts:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access"
            )

        # Fetch transactions from the database
        transactions = transaction_crud(
            db=session,
            account_id=account_id,
        )

        return TransactionReturnList(
            success=True,
            status="200",
            message="Transactions retrieved successfully",
            data=transactions,
        )
    except HTTPException:
        raise
    except Exception as e:
        if settings.DEBUG:
            logger.error(f"Error fetching transactions: {e}")
        else:
            logger.error(f"Error fetching transactions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
